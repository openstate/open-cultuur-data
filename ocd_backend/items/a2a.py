from datetime import datetime

from ocd_backend.log import get_source_logger
from ocd_backend.items import BaseItem

log = get_source_logger('item')


class A2AItem(BaseItem):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'a2a': 'http://Mindbus.nl/A2A'
    }

    def _get_node_or_none(self, xpath_expression, node=None):
        """
        Returns the requested node based on the xpath expression. Returns None
        if the node did not exist.
        """
        if node is None:
            node = self.original_item
        return node.find(xpath_expression, namespaces=self.namespaces)

    def _get_text_or_none(self, xpath_expression, start_node=None):
        """
        Returns the text node(s) in the node requested based on the xpath
        expression. Returns None if no text nodes could be found. Optionally
        you can specify a start_node for the expression.
        """
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
        return id

    def _get_event_type(self):
        """
        Returns the event type for an A2A record. This describes what kind
        of event occured.
        """
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
        """
        Returns the place of an event. This describes where the event occured.
        """
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
        """
        Returns the name of the institution that owns this A2A record.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:InstitutionName'
        )

    def _get_main_persons(self):
        """
        Returns the name(s) of the main person(s) involved in the event.
        """
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

        # concat all names of the main and involved persons in the event
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
            if personPid in mainPersonKeyRefs:
                mainPersons.append(
                    ' '.join(filter(None, (personVN, personVV, personAN)))
                )

        return mainPersons, allPersons

    def _get_title(self, mainPersons, eventType):
        """
        Returns the title of the event. The title of the event is a combination
        of the list of main persons and the event type, which you need to
        specify.
        """
        title = ', '.join(filter(None, (eventType, ' & '.join(mainPersons))))
        return unicode(title)

    def _get_source_type(self):
        """
        Returns the type of the source of this A2A record.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceType'
        )

    def _get_source_place(self):
        """
        Returns the place of the source.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourcePlace/a2a:Place'
        )

    def _get_description(
        self, institutionName, sourceType, sourcePlace, allPersons
    ):
        """
        Returns a description of the A2A event. This description is constructed
        The description is a concatenation of all persons involved, as well as
        the source type, source place and the name of the institution which
        is the owner of the A2A record.
        """
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
        """
        Returns the date of the event, or None when it was not available/
        """
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
                    else:
                        parsedDate = datetime.strptime(
                            eventDateMonth + "-" + eventDateYear, '%m-%Y'
                        )
                        parsedGranularity = 6
                else:
                    parsedDate = datetime.strptime(
                        eventDateYear, '%Y'
                    )
                    parsedGranularity = 4
        return parsedDate, parsedGranularity

    def _get_media_urls(self):
        """
        Returns the media urls of the A2A record, if avaiable. The media urls
        are the scans of the certificates.
        """
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
        else:   # multiple scans?
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
        """
        Returns the document number of the A2A record, if available.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:DocumentNumber'
        )

    def _get_book(self):
        """
        Returns the book from which this A2A record was extracted.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:Book'
        )

    def _get_collection(self):
        """
        Returns the collection, which this A2A record is a part of, if
        available
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:Collection'
        )

    def _get_registry_number(self):
        """
        Returns the registry number for this A2A record, if available.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:RegistryNumber'
        )

    def _get_archive_number(self):
        """
        Returns the archive number of this A2A record, if available.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:Archive'
        )

    def _get_source_remark(self):
        """
        Returns the source remark for this A2A record, if avaiable.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceRemark/'
            'a2a:Value'
        )

    def _get_authors(self):
        """
        Returns the authors of the certificate. Currently not implemented.
        """
        return []

    def get_combined_index_data(self):
        combined_index_data = {}

        eventType = self._get_event_type()

        eventPlace = self._get_event_place()

        institutionName = self._get_institution_name()

        mainPersons, allPersons = self._get_main_persons()

        combined_index_data['title'] = self._get_title(mainPersons, eventType)

        sourceType = self._get_source_type()

        sourcePlace = self._get_source_place()

        description = self._get_description(
            institutionName, sourceType, sourcePlace, allPersons
        )
        if description:
            combined_index_data['description'] = unicode(description)

        parsedDate, parsedGranularity = self._get_date_and_granularity()
        combined_index_data['date'] = parsedDate
        combined_index_data['date_granularity'] = parsedGranularity

        combined_index_data['authors'] = self._get_authors()

        combined_index_data['media_urls'] = self._get_media_urls()

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        eventType = self._get_event_type()
        text_items.append(eventType)

        eventPlace = self._get_event_place()
        text_items.append(eventPlace)

        sourceType = self._get_source_type()
        text_items.append(sourceType)

        sourcePlace = self._get_source_place()
        text_items.append(sourcePlace)

        institutionName = self._get_institution_name()
        text_items.append(institutionName)

        documentNumber = self._get_document_number()
        text_items.append(documentNumber)

        bookName = self._get_book()
        text_items.append(bookName)

        collectieName = self._get_collection()
        text_items.append(collectieName)

        registrationNumber = self._get_registry_number()
        text_items.append(registrationNumber)

        archiveNumber = self._get_archive_number()
        text_items.append(archiveNumber)

        sourceRemark = self._get_source_remark()
        text_items.append(sourceRemark)

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
