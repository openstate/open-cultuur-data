from datetime import datetime
from ocd_backend.log import get_source_logger
from ocd_backend.items import BaseItem

log = get_source_logger('loader')

class OpenArchievenItem(BaseItem):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'a2a': 'http://Mindbus.nl/A2A'
    }

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(xpath_expression, namespaces=self.namespaces)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def get_original_object_id(self):
        id=self._get_text_or_none('.//oai:header/oai:identifier')
        log.info('Processing record %s' % id)
        return id

    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        archive,identifier=original_id.split(":")
        return {
            'html': 'http://www.openarch.nl/show.php?archive=%s&identifier=%s' % (archive,identifier),
            'xml': 'http://api.openarch.nl/oai-pmh/?verb=GetRecord&metadataPrefix=oai_a2a&identifier=%s' % original_id
        }

    def get_rights(self):
        return u'Creative Commons Zero Public Domain'

    def get_collection(self):
        return u'Open Archieven'

    def get_combined_index_data(self):
        combined_index_data = {}

        # soort gebeurtenis, bijv. Geboorte
        # <a2a:Event eid="Event1" a2a:EventType="Overlijden">
        eventType = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Event','{http://Mindbus.nl/A2A}EventType')
        eventType.replace("other:","")

        # plaats van de gebeurtenis
        eventPlace = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Event/a2a:EventPlace','{http://Mindbus.nl/A2A}Place')

        # naam van de archiefinstelling
        institutionName = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference','{http://Mindbus.nl/A2A}InstitutionName')

        # bepalen van de hoofdpersonen bij de gebeurtenis voor gebruik in title (mainPersonKeyRefs) op basis van RelationEP
        mainPersonKeyRefs = []
        relations = self.original_item.findall('.//oai:metadata/a2a:A2A/a2a:RelationEP', namespaces=self.namespaces)
        if relations is not None:
            for relation in relations:
               relationType=relation.get("{http://Mindbus.nl/A2A}RelationType")
               personKeyRef=relation.get("{http://Mindbus.nl/A2A}PersonKeyRef")
               if relationType == "Kind":
                    mainPersonKeyRefs.append(personKeyRef)
               if relationType == "Overledene":
                    mainPersonKeyRefs.append(personKeyRef)
               if relationType == "Werknemer":
                    mainPersonKeyRefs.append(personKeyRef)
               if relationType == "Bruid":
                    mainPersonKeyRefs.append(personKeyRef)
               if relationType == "Bruidegom":
                    mainPersonKeyRefs.append(personKeyRef)
               if relationType == "Geregistreerde":
                    mainPersonKeyRefs.append(personKeyRef)

        # samenvoegen van alle namen van hoofdpersonen (mainPersons) en betrokken personen (allPersons)
        mainPersons = []
        allPersons = []
        persons = self.original_item.findall('.//oai:metadata/a2a:A2A/a2a:Person', namespaces=self.namespaces)
        if persons is not None:
            for person in persons:
                personName= person.find('.//a2a:PersonName', namespaces=self.namespaces)
                personVN = personName.get('{http://Mindbus.nl/A2A}PersonNameFirstName')
                personVV = personName.get('{http://Mindbus.nl/A2A}PersonNamePrefixLastName')
                personAN = personName.get('{http://Mindbus.nl/A2A}PersonNameLastName')
                allPersons.append(' '.join(filter(None, (personVN, personVV, personAN))))
                personPid = person.get('pid')
                if personPid in mainPersonKeyRefs:
                    mainPersons.append(' '.join(filter(None, (personVN, personVV, personAN))))

        # title wordt samengesteld uit het eventtype, naam/namen van de hoofdpersoon/hoofdpersonen
        title = ', '.join(filter(None, (eventType, ' & '.join(mainPersons))))
        combined_index_data['title'] = unicode(title)

        # bron type
        sourceType = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source','{http://Mindbus.nl/A2A}SourceType')

        # plaats van de bron
        sourcePlace = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourcePlace','{http://Mindbus.nl/A2A}Place')

        # in description worden alle persoonsnamen, de sourceType, sourcePlace, InstitutionName samengevoegd
        description = ', '.join(filter(None, (institutionName,sourceType,sourcePlace,' & '.join(allPersons) )))
        if description:
            combined_index_data['description'] = unicode(description)

        # datum van de gebeurtenis, opgedeeld in dag, maand en jaar, niet altijd (allemaal) aanwezig ...
        eventDate = None
        eventDateObj=self.original_item.find('.//oai:metadata/a2a:A2A/a2a:Event/a2a:EventDate', namespaces=self.namespaces)
        if eventDateObj is not None:
            eventDateDay=eventDateObj.get('{http://Mindbus.nl/A2A}Day')
            eventDateMonth=eventDateObj.get('{http://Mindbus.nl/A2A}Month')
            eventDateYear=eventDateObj.get('{http://Mindbus.nl/A2A}Year')
            if eventDateYear is not None:
               if eventDateMonth is not None and int(eventDateMonth)>0 and int(eventDateMonth)<13:
                  if eventDateDay is not None and int(eventDateDay)>0 and int(eventDateDay)<32:
                     combined_index_data['date'] = datetime.strptime(eventDateDay+"-"+eventDateMonth+"-"+eventDateYear, '%d-%m-%Y')
                     combined_index_data['date_granularity'] = 8
                  else:    # geen dag
                     combined_index_data['date'] = datetime.strptime(eventDateMonth+"-"+eventDateYear, '%m-%Y')
                     combined_index_data['date_granularity'] = 6
               else:    # geen maand/dag
                  combined_index_data['date'] = datetime.strptime(eventDateYear, '%Y')
                  combined_index_data['date_granularity'] = 4

        # omdat dit meta-data van naar archieven overgebrachte overheidsdocumenten zijn is er geen auteur

        combined_index_data['media_urls'] = []

        # available scans (1 or more...)
        scanUriPreview = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceAvailableScans','{http://Mindbus.nl/A2A}UriPreview')
        if scanUriPreview is not None:
           combined_index_data['media_urls'].append({
              'original_url': scanUriPreview,
              'content_type': 'image/jpeg'
              })
        else:   # meerdere scans?
            scans = self.original_item.findall('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceAvailableScans/a2a:Scan', namespaces=self.namespaces)
            if scans is not None:
                for scan in scans:
                   scanUriPreview=scan.get('{http://Mindbus.nl/A2A}UriPreview)')
                   if scanUriPreview is not None:
                      combined_index_data['media_urls'].append({
                         'original_url': scanUriPreview,
                         'content_type': 'image/jpeg'
                      })

        return combined_index_data

    def get_index_data(self):
        return {}


    def get_attribute(self,xpath,attrib):
        obj=self.original_item.find(xpath, namespaces=self.namespaces)
        if obj is not None:
            return obj.get(attrib)
        else:
            return None


    def get_all_text(self):
        text_items = []

        # gebeurtenis type
        eventType = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Event','{http://Mindbus.nl/A2A}EventType')
        if eventType is not None:
              eventType.replace("other:","")
              text_items.append(eventType)

        # plaats van de gebeurtenis
        eventPlace = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Event/a2a:EventPlace','{http://Mindbus.nl/A2A}Place')
        if eventPlace is not None:
              text_items.append(eventPlace)

        # bron type
        sourceType = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source','{http://Mindbus.nl/A2A}SourceType')
        if sourceType is not None:
              text_items.append(sourceType)

        # plaats van de bron
        sourcePlace = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourcePlace','{http://Mindbus.nl/A2A}Place')
        if sourcePlace is not None:
              text_items.append(sourcePlace)

        # naam van de archiefinstelling
        institutionName = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference','{http://Mindbus.nl/A2A}InstitutionName')
        if institutionName is not None:
              text_items.append(institutionName)

        # document nummer
        documentNumber = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference','{http://Mindbus.nl/A2A}DocumentNumber')
        if documentNumber is not None:
              text_items.append(documentNumber)

        # naam van boek
        bookName = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference','{http://Mindbus.nl/A2A}Book')
        if bookName is not None:
              text_items.append(bookName)

        # naam van collectie
        collectieName = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference','{http://Mindbus.nl/A2A}Collection')
        if collectieName is not None:
              text_items.append(collectieName)

        # registratie nummer
        registrationNumber = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference','{http://Mindbus.nl/A2A}RegistryNumber')
        if registrationNumber is not None:
              text_items.append(registrationNumber)

        # archief nummer
        archiveNumber = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference','{http://Mindbus.nl/A2A}Archive')
        if archiveNumber is not None:
              text_items.append(archiveNumber)

        # bron opmerking
        sourceRemark = self.get_attribute('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceRemark','{http://Mindbus.nl/A2A}Value')
        if sourceRemark is not None:
              text_items.append(sourceRemark)

        # personen
        persons = self.original_item.findall('.//oai:metadata/a2a:A2A/a2a:Person', namespaces=self.namespaces)
        if persons is not None:
            for person in persons:
                personName= person.find('.//a2a:PersonName', namespaces=self.namespaces)
                personVN = personName.get('{http://Mindbus.nl/A2A}PersonNameFirstName')
                personVV = personName.get('{http://Mindbus.nl/A2A}PersonNamePrefixLastName')
                personAN = personName.get('{http://Mindbus.nl/A2A}PersonNameLastName')
                text_items.append(' '.join(filter(None, (personVN, personVV, personAN))))

        return u' '.join([ti for ti in text_items if ti is not None])
