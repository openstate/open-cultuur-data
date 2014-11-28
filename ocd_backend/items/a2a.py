from datetime import datetime
from pprint import pprint

from ocd_backend.log import get_source_logger
from ocd_backend.items import BaseItem

log = get_source_logger('loader')


class A2AItem(BaseItem):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'a2a': 'http://Mindbus.nl/A2A'
    }

    def _get_node_or_none(self, xpath_expression, node=None):
        if node is None:
            node = self.original_item
        return node.find(xpath_expression, namespaces=self.namespaces)

    def _get_text_or_none(self, xpath_expression, start_node=None):
        if start_node is None:
            start_node = self.original_item
        node = start_node.find(
            xpath_expression, namespaces=self.namespaces
        )
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def get_original_object_id(self):
        id = self._get_text_or_none('.//oai:header/oai:identifier')
        log.info('Processing record %s' % id)
        return id

    def get_combined_index_data(self):
        combined_index_data = {}

        log.info('Getting combined index data ...')

        # soort gebeurtenis, bijv. Geboorte
        # <a2a:Event eid="Event1" a2a:EventType="Overlijden">
        eventRecord = self._get_node_or_none(
            './/oai:metadata/a2a:A2A/a2a:Event'
        )
        eventType = None
        if eventRecord is not None:
            eventTypeRecord = self._get_node_or_none(
                './a2a:EventType', eventRecord
            )
            if eventTypeRecord is not None:
                eventType = eventTypeRecord.text

        eventType = eventType.replace('other:', '')

        # plaats van de gebeurtenis
        eventPlace = None
        eventPlaceRecord = self._get_node_or_none(
            './a2a:EventPlace/a2a:Place', eventRecord
        )
        if eventPlaceRecord is not None:
            eventPlace = eventPlaceRecord.text

        # naam van de archiefinstelling
        institutionName = self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:InstitutionName'
        )

        # bepalen van de hoofdpersonen bij de gebeurtenis voor gebruik in title
        # (mainPersonKeyRefs) op basis van RelationEP
        mainPersonKeyRefs = []
        relations = self.original_item.findall(
            './/oai:metadata/a2a:A2A/a2a:RelationEP',
            namespaces=self.namespaces
        )
        if relations is None:
            relations = []
        for relation in relations:
            relationType = self._get_text_or_none(
                './a2a:RelationType',
                relation
            )
            personKeyRef = self._get_text_or_none(
                './a2a:PersonKeyRef',
                relation
            )
            if relationType in [
                "Kind", "Overledene", "Werknemer", "Bruid", "Bruidegom",
                "Geregistreerde"
            ]:
                mainPersonKeyRefs.append(personKeyRef)

        # samenvoegen van alle namen van hoofdpersonen (mainPersons) en
        # betrokken personen (allPersons)
        mainPersons = []
        allPersons = []
        persons = self.original_item.findall(
            './/oai:metadata/a2a:A2A/a2a:Person', namespaces=self.namespaces
        )
        if persons is None:
            persons = []
        for person in persons:
            personName = self._get_node_or_none(
                './/a2a:PersonName', person
            )
            personVN = self._get_text_or_none(
                './/a2a:PersonNameFirstName', personName
            )
            personVV = self._get_text_or_none(
                './/a2a:PersonNamePrefixLastName', personName
            )
            personAN = self._get_text_or_none(
                './/a2a:PersonNameLastName', personName
            )
            allPersons.append(
                ' '.join(filter(None, (personVN, personVV, personAN)))
            )
            personPid = person.get('pid')
            pprint(personPid)
            if personPid in mainPersonKeyRefs:
                mainPersons.append(
                    ' '.join(filter(None, (personVN, personVV, personAN)))
                )

        # title wordt samengesteld uit het eventtype, naam/namen van de
        # hoofdpersoon/hoofdpersonen
        title = ', '.join(filter(None, (eventType, ' & '.join(mainPersons))))
        combined_index_data['title'] = unicode(title)

        # bron type
        sourceType = self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceType'
        )

        # plaats van de bron
        sourcePlace = self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourcePlace/a2a:Place'
        )

        # in description worden alle persoonsnamen, de sourceType, sourcePlace,
        # InstitutionName samengevoegd
        description = ', '.join(
            filter(
                None, (
                    institutionName, sourceType, sourcePlace, ' & '.join(
                        allPersons
                    )
                )
            )
        )
        if description:
            combined_index_data['description'] = unicode(description)

        # datum van de gebeurtenis, opgedeeld in dag, maand en jaar, niet
        # altijd (allemaal) aanwezig ...
        eventDate = None
        eventDateObj = self._get_node_or_none(
            './/oai:metadata/a2a:A2A/a2a:Event/a2a:EventDate'
        )
        if eventDateObj is not None:
            eventDateDay = self._get_text_or_none(
                './a2a:Day', eventDateObj
            )
            eventDateMonth = self._get_text_or_none(
                './a2a:Month', eventDateObj
            )
            eventDateYear = self._get_text_or_none(
                './a2a:Year', eventDateObj
            )
            if eventDateYear is not None:
                if (
                    eventDateMonth is not None and int(eventDateMonth) > 0 and
                    int(eventDateMonth) < 13
                ):
                    if (
                        eventDateDay is not None and
                        int(eventDateDay) > 0 and
                        int(eventDateDay) < 32
                    ):
                        combined_index_data['date'] = datetime.strptime(
                            eventDateDay + "-" + eventDateMonth + "-" +
                            eventDateYear,
                            '%d-%m-%Y'
                        )
                        combined_index_data['date_granularity'] = 8
                    else:    # geen dag
                        combined_index_data['date'] = datetime.strptime(
                            eventDateMonth + "-" + eventDateYear, '%m-%Y'
                        )
                        combined_index_data['date_granularity'] = 6
                else:    # geen maand/dag
                    combined_index_data['date'] = datetime.strptime(
                        eventDateYear, '%Y'
                    )
                    combined_index_data['date_granularity'] = 4

        # omdat dit meta-data van naar archieven overgebrachte
        # overheidsdocumenten zijn is er geen auteur

        combined_index_data['media_urls'] = []

        # available scans (1 or more...)
        scanUriPreview = self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceAvailableScans/'
            'a2a:UriPreview'
        )
        if scanUriPreview is not None:
            combined_index_data['media_urls'].append({
                'original_url': scanUriPreview,
                'content_type': 'image/jpeg'
            })
        else:   # meerdere scans?
            scans = self.original_item.findall(
                './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceAvailableScans/'
                'a2a:Scan', namespaces=self.namespaces
            )
            if scans is None:
                scans = []
            for scan in scans:
                scanUriPreview = self._get_text_or_none(
                    'a2a:UriPreview', scan
                )
                if scanUriPreview is not None:
                    combined_index_data['media_urls'].append({
                        'original_url': scanUriPreview,
                        'content_type': 'image/jpeg'
                    })

        pprint(combined_index_data)
        return combined_index_data

    def get_index_data(self):
        return {}

    def get_attribute(self, xpath, attrib):
        obj = self.original_item.find(xpath, namespaces=self.namespaces)
        if obj is not None:
            return obj.get(attrib)
        else:
            return None

    def get_all_text(self):
        text_items = []

        # gebeurtenis type
        eventType = self.get_attribute(
            './/oai:metadata/a2a:A2A/a2a:Event',
            '{http://Mindbus.nl/A2A}EventType'
        )
        if eventType is not None:
            eventType.replace("other:", "")
            text_items.append(eventType)

        # plaats van de gebeurtenis
        eventPlace = self.get_attribute(
            './/oai:metadata/a2a:A2A/a2a:Event/a2a:EventPlace',
            '{http://Mindbus.nl/A2A}Place'
        )
        if eventPlace is not None:
            text_items.append(eventPlace)

        # bron type
        sourceType = self.get_attribute(
            './/oai:metadata/a2a:A2A/a2a:Source',
            '{http://Mindbus.nl/A2A}SourceType'
        )
        if sourceType is not None:
            text_items.append(sourceType)

        # plaats van de bron
        sourcePlace = self.get_attribute(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourcePlace',
            '{http://Mindbus.nl/A2A}Place'
        )
        if sourcePlace is not None:
            text_items.append(sourcePlace)

        # naam van de archiefinstelling
        institutionName = self.get_attribute(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference',
            '{http://Mindbus.nl/A2A}InstitutionName'
        )
        if institutionName is not None:
            text_items.append(institutionName)

        # document nummer
        documentNumber = self.get_attribute(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference',
            '{http://Mindbus.nl/A2A}DocumentNumber'
        )
        if documentNumber is not None:
            text_items.append(documentNumber)

        # naam van boek
        bookName = self.get_attribute(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference',
            '{http://Mindbus.nl/A2A}Book'
        )
        if bookName is not None:
            text_items.append(bookName)

        # naam van collectie
        collectieName = self.get_attribute(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference',
            '{http://Mindbus.nl/A2A}Collection'
        )
        if collectieName is not None:
            text_items.append(collectieName)

        # registratie nummer
        registrationNumber = self.get_attribute(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference',
            '{http://Mindbus.nl/A2A}RegistryNumber'
        )
        if registrationNumber is not None:
            text_items.append(registrationNumber)

        # archief nummer
        archiveNumber = self.get_attribute(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference',
            '{http://Mindbus.nl/A2A}Archive'
        )
        if archiveNumber is not None:
            text_items.append(archiveNumber)

        # bron opmerking
        sourceRemark = self.get_attribute(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceRemark',
            '{http://Mindbus.nl/A2A}Value'
        )
        if sourceRemark is not None:
            text_items.append(sourceRemark)

        # personen
        persons = self.original_item.findall(
            './/oai:metadata/a2a:A2A/a2a:Person',
            namespaces=self.namespaces
        )
        if persons is not None:
            for person in persons:
                personName = person.find(
                    './/a2a:PersonName', namespaces=self.namespaces
                )
                personVN = personName.get(
                    '{http://Mindbus.nl/A2A}PersonNameFirstName'
                )
                personVV = personName.get(
                    '{http://Mindbus.nl/A2A}PersonNamePrefixLastName'
                )
                personAN = personName.get(
                    '{http://Mindbus.nl/A2A}PersonNameLastName'
                )
                text_items.append(
                    ' '.join(filter(None, (personVN, personVV, personAN)))
                )

        return u' '.join([ti for ti in text_items if ti is not None])
