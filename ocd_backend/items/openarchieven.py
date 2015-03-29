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
            'json': 'http://api.openarch.nl/1.0/records/show.json?archive=%s&identifier=%s' % (archive,identifier),
            'xml': 'http://api.openarch.nl/oai-pmh/?verb=GetRecord&metadataPrefix=oai_a2a&identifier=%s' % original_id
        }

    def get_rights(self):
        return u'Creative Commons Zero Public Domain'

    def get_collection(self):
        return u'Open Archieven'

    def get_combined_index_data(self):
        combined_index_data = {}

        # soort gebeurtenis, bijv. Geboorte
        eventType = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Event/a2a:EventType').replace("other:","")

        # plaats van de gebeurtenis
        eventPlace = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Event/a2a:EventPlace/a2a:Place')

        # naam van de archiefinstelling
        institutionName = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/a2a:InstitutionName')

        # bepalen van de hoofdpersonen bij de gebeurtenis voor gebruik in title (mainPersonKeyRefs) op basis van RelationEP
        mainPersonKeyRefs = []
        relations = self.original_item.findall('.//oai:metadata/a2a:A2A/a2a:RelationEP', namespaces=self.namespaces)
        if relations is not None:
            for relation in relations:            	
               relationType = relation.find('.//a2a:RelationType', namespaces=self.namespaces).text
               personKeyRef = relation.find('.//a2a:PersonKeyRef', namespaces=self.namespaces).text
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
                personName = person.find('.//a2a:PersonName', namespaces=self.namespaces)
                personVN = self._get_text_or_none_sub(personName,'.//a2a:PersonNameFirstName')
                personVV = self._get_text_or_none_sub(personName,'.//a2a:PersonNamePrefixLastName')
                personAN = self._get_text_or_none_sub(personName,'.//a2a:PersonNameLastName')
                allPersons.append(' '.join(filter(None, (personVN, personVV, personAN))))
                personPid = person.get('pid')
                if personPid in mainPersonKeyRefs:
                    mainPersons.append(' '.join(filter(None, (personVN, personVV, personAN))))

        # title wordt samengesteld uit het eventtype, naam/namen van de hoofdpersoon/hoofdpersonen
        title = ', '.join(filter(None, (eventType, ' & '.join(mainPersons))))
        combined_index_data['title'] = unicode(title)

        # bron type
        sourceType = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceType').replace("other:","")

        # plaats van de bron
        sourcePlace = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourcePlace/a2a:Place')

        # in description worden alle persoonsnamen, de sourceType, sourcePlace, InstitutionName samengevoegd
        description = ', '.join(filter(None, (institutionName,sourceType,sourcePlace,' & '.join(allPersons) )))
        if description:
            combined_index_data['description'] = unicode(description)

        # datum van de gebeurtenis, opgedeeld in dag, maand en jaar, niet altijd (allemaal) aanwezig ...
        eventDate = None
        eventDateObj=self.original_item.find('.//oai:metadata/a2a:A2A/a2a:Event/a2a:EventDate', namespaces=self.namespaces)
        if eventDateObj is not None:
            eventDateDay=self._get_text_or_none_sub(eventDateObj,'.//a2a:Day')
            eventDateMonth=self._get_text_or_none_sub(eventDateObj,'.//a2a:Month')
            eventDateYear=self._get_text_or_none_sub(eventDateObj,'.//a2a:Year')
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
        scanUriPreview = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceAvailableScans/a2a:Scan/a2a:UriPreview')
        if scanUriPreview is not None:
           combined_index_data['media_urls'].append({
              'original_url': scanUriPreview,
              'content_type': 'image/jpeg'
              })
        else:   # meerdere scans?
            scans = self.original_item.findall('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceAvailableScans/a2a:Scan', namespaces=self.namespaces)
            if scans is not None:
                for scan in scans:
                   scanUriPreview=scan.get('a2a:UriPreview)')
                   if scanUriPreview is not None:
                      combined_index_data['media_urls'].append({
                         'original_url': scanUriPreview,
                         'content_type': 'image/jpeg'
                      })

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # gebeurtenis type
        eventType = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Event/a2a:EventType')
        if eventType is not None:
              text_items.append(eventType.replace("other:",""))

        # plaats van de gebeurtenis
        eventPlace = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Event/a2a:EventPlace/a2a:Place')
        if eventPlace is not None:
              text_items.append(eventPlace)

        # bron type
        sourceType = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceType')
        if sourceType is not None:
              text_items.append(sourceType.replace("other:",""))

        # plaats van de bron
        sourcePlace = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourcePlace/a2a:Place')
        if sourcePlace is not None:
              text_items.append(sourcePlace)

        # naam van de archiefinstelling
        institutionName = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/a2a:InstitutionName')
        if institutionName is not None:
              text_items.append(institutionName)

        # document nummer
        documentNumber = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/a2a:DocumentNumber')
        if documentNumber is not None:
              text_items.append(documentNumber)

        # naam van boek
        bookName = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/a2a:Book')
        if bookName is not None:
              text_items.append(bookName)

        # naam van collectie
        collectieName = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/a2a:Collection')
        if collectieName is not None:
              text_items.append(collectieName)

        # registratie nummer
        registrationNumber = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/a2aRegistryNumber')
        if registrationNumber is not None:
              text_items.append(registrationNumber)

        # archief nummer
        archiveNumber = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/a2a:Archive')
        if archiveNumber is not None:
              text_items.append(archiveNumber)

        # bron opmerking
        sourceRemark = self._get_text_or_none('.//oai:metadata/a2a:A2A/a2a:Source/a2a:SourceRemark/a2a:Value')
        if sourceRemark is not None:
              text_items.append(sourceRemark)

        # personen
        persons = self.original_item.findall('.//oai:metadata/a2a:A2A/a2a:Person', namespaces=self.namespaces)
        if persons is not None:
            for person in persons:
                personName= person.find('.//a2a:PersonName', namespaces=self.namespaces)
                personVN = self._get_text_or_none_sub(personName,'.//a2a:PersonNameFirstName')
                personVV = self._get_text_or_none_sub(personName,'.//a2a:PersonNamePrefixLastName')
                personAN = self._get_text_or_none_sub(personName,'.//a2a:PersonNameLastName')
                text_items.append(' '.join(filter(None, (personVN, personVV, personAN))))

        return u' '.join([ti for ti in text_items if ti is not None])


    def _get_text_or_none_sub(self, sub, xpath_expression):
        node = sub.find(xpath_expression, namespaces=self.namespaces)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None
