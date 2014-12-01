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

    def _get_event_type(self):
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

        return eventType

    def _get_event_place(self):
        # plaats van de gebeurtenis
        eventRecord = self._get_node_or_none(
            './/oai:metadata/a2a:A2A/a2a:Event'
        )
        eventPlace = None
        eventPlaceRecord = self._get_node_or_none(
            './a2a:EventPlace/a2a:Place', eventRecord
        )
        if eventPlaceRecord is not None:
            eventPlace = eventPlaceRecord.text

        return eventPlace

    def _get_institution_name(self):
        # naam van de archiefinstelling
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:InstitutionName'
        )

    def _get_main_persons(self):
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

        return mainPersons, allPersons

    def _get_title(self, mainPersons, eventType):
        # title wordt samengesteld uit het eventtype, naam/namen van de
        # hoofdpersoon/hoofdpersonen
        title = ', '.join(filter(None, (eventType, ' & '.join(mainPersons))))
        return unicode(title)

    def _get_source_type(self):
        # bron type
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceType'
        )

    def _get_source_place(self):
        # plaats van de bron
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourcePlace/a2a:Place'
        )

    def _get_description(
        self, institutionName, sourceType, sourcePlace, allPersons
    ):
        # in description worden alle persoonsnamen, de sourceType, sourcePlace,
        # InstitutionName samengevoegd
        return ', '.join(
            filter(
                None, (
                    institutionName, sourceType, sourcePlace, ' & '.join(
                        allPersons
                    )
                )
            )
        )

    def _get_date_and_granularity(self):
        # datum van de gebeurtenis, opgedeeld in dag, maand en jaar, niet
        # altijd (allemaal) aanwezig ...
        parsedDate = None
        parsedGranularity = 0

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
                        parsedDate = datetime.strptime(
                            eventDateDay + "-" + eventDateMonth + "-" +
                            eventDateYear,
                            '%d-%m-%Y'
                        )
                        parsedGranularity = 8
                    else:    # geen dag
                        parsedDate = datetime.strptime(
                            eventDateMonth + "-" + eventDateYear, '%m-%Y'
                        )
                        parsedGranularity = 6
                else:    # geen maand/dag
                    parsedDate = datetime.strptime(
                        eventDateYear, '%Y'
                    )
                    parsedGranularity = 4
        return parsedDate, parsedGranularity

    def _get_media_urls(self):
        # available scans (1 or more...)
        media_urls = []

        scanUriPreview = self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceAvailableScans/'
            'a2a:UriPreview'
        )
        if scanUriPreview is not None:
            media_urls.append({
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
                    media_urls.append({
                        'original_url': scanUriPreview,
                        'content_type': 'image/jpeg'
                    })

        return media_urls

    def _get_document_number(self):
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:DocumentNumber'
        )

    def _get_book(self):
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:Book'
        )

    def _get_collection(self):
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:Collection'
        )

    def _get_registry_number(self):
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:RegistryNumber'
        )

    def _get_archive_number(self):
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:Archive'
        )

    def _get_source_remark(self):
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceRemark/'
            'a2a:Value'
        )

    def _get_authors(self):
        return []

    def get_combined_index_data(self):
        combined_index_data = {}

        log.info('Getting combined index data ...')

        # soort gebeurtenis, bijv. Geboorte
        eventType = self._get_event_type()

        # plaats van de gebeurtenis
        eventPlace = self._get_event_place()

        # naam van de archiefinstelling
        institutionName = self._get_institution_name()

        # bepalen van de hoofdpersonen bij de gebeurtenis voor gebruik in title
        # (mainPersonKeyRefs) op basis van RelationEP
        mainPersons, allPersons = self._get_main_persons()

        # title wordt samengesteld uit het eventtype, naam/namen van de
        # hoofdpersoon/hoofdpersonen
        combined_index_data['title'] = self._get_title(mainPersons, eventType)

        # bron type
        sourceType = self._get_source_type()

        # plaats van de bron
        sourcePlace = self._get_source_place()

        # in description worden alle persoonsnamen, de sourceType, sourcePlace,
        # InstitutionName samengevoegd
        description = self._get_description(
            institutionName, sourceType, sourcePlace, allPersons
        )
        if description:
            combined_index_data['description'] = unicode(description)

        # datum van de gebeurtenis, opgedeeld in dag, maand en jaar, niet
        # altijd (allemaal) aanwezig ...
        parsedDate, parsedGranularity = self._get_date_and_granularity()
        if parsedDate is not None:
            combined_index_data['date'] = parsedDate
            combined_index_data['date_granularity'] = parsedGranularity

        # omdat dit meta-data van naar archieven overgebrachte
        # overheidsdocumenten zijn is er geen auteur
        combined_index_data['authors'] = self._get_authors()

        # available scans (1 or more...)
        combined_index_data['media_urls'] = self._get_media_urls()

        pprint(combined_index_data)
        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # gebeurtenis type
        eventType = self._get_event_type()
        text_items.append(eventType)

        # plaats van de gebeurtenis
        eventPlace = self._get_event_place()
        text_items.append(eventPlace)

        # bron type
        sourceType = self._get_source_type()
        text_items.append(sourceType)

        # plaats van de bron
        sourcePlace = self._get_source_place()
        text_items.append(sourcePlace)

        # naam van de archiefinstelling
        institutionName = self._get_institution_name()
        text_items.append(institutionName)

        # document nummer
        documentNumber = self._get_document_number()
        text_items.append(documentNumber)

        # naam van boek
        bookName = self._get_book()
        text_items.append(bookName)

        # naam van collectie
        collectieName = self._get_collection()
        text_items.append(collectieName)

        # registratie nummer
        registrationNumber = self._get_registry_number()
        text_items.append(registrationNumber)

        # archief nummer
        archiveNumber = self._get_archive_number()
        text_items.append(archiveNumber)

        # bron opmerking
        sourceRemark = self._get_source_remark()
        text_items.append(sourceRemark)

        # personen
        persons = self.original_item.findall(
            './/oai:metadata/a2a:A2A/a2a:Person',
            namespaces=self.namespaces
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
            text_items.append(
                ' '.join(filter(None, (personVN, personVV, personAN)))
            )

        return u' '.join([ti for ti in text_items if ti is not None])
