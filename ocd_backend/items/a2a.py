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
            xpath_expression, namespaces=self.namespaces)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def get_original_object_id(self):
        return self._get_text_or_none('.//oai:header/oai:identifier')

    def _get_event_type(self):
        """
        Returns the event type for an A2A record. This describes what kind
        of event occured.
        """
        event_record = self._get_node_or_none(
            './/oai:metadata/a2a:A2A/a2a:Event')
        event_type = None
        if event_record is not None:
            event_type_record = self._get_node_or_none(
                './a2a:EventType', event_record)
            if event_type_record is not None:
                event_type = event_type_record.text.replace('other:', '')

        return event_type

    def _get_event_place(self):
        """
        Returns the place of an event. This describes where the event occured.
        """
        event_record = self._get_node_or_none(
            './/oai:metadata/a2a:A2A/a2a:Event')
        event_place = None
        event_place_record = self._get_node_or_none(
            './a2a:EventPlace/a2a:Place', event_record)
        if event_place_record is not None:
            event_place = event_place_record.text

        return event_place

    def _get_institution_name(self):
        """
        Returns the name of the institution that owns this A2A record.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:InstitutionName')

    def _get_main_persons(self):
        """
        Returns the name(s) of the main person(s) involved in the event.
        """
        main_person_key_refs = []
        relations = self.original_item.findall(
            './/oai:metadata/a2a:A2A/a2a:RelationEP',
            namespaces=self.namespaces)
        if relations is None:
            relations = []
        for relation in relations:
            relation_type = self._get_text_or_none(
                './a2a:RelationType', relation)
            person_key_ref = self._get_text_or_none(
                './a2a:PersonKeyRef',
                relation)
            if relation_type in [
                    "Kind", "Overledene", "Werknemer", "Bruid", "Bruidegom",
                    "Geregistreerde"]:
                main_person_key_refs.append(person_key_ref)

        # concat all names of the main and involved persons in the event
        main_persons = []
        all_persons = []
        persons = self.original_item.findall(
            './/oai:metadata/a2a:A2A/a2a:Person', namespaces=self.namespaces)
        if persons is None:
            persons = []
        for person in persons:
            person_name = self._get_node_or_none(
                './/a2a:PersonName', person)
            person_vn = self._get_text_or_none(
                './/a2a:PersonNameFirstName', person_name)
            person_vv = self._get_text_or_none(
                './/a2a:PersonNamePrefixLastName', person_name)
            person_an = self._get_text_or_none(
                './/a2a:PersonNameLastName', person_name)
            full_name = ' '.join(
                filter(None, (person_vn, person_vv, person_an)))
            all_persons.append(full_name)
            if person.get('pid') in main_person_key_refs:
                main_persons.append(full_name)

        return main_persons, all_persons

    def _get_title(self, main_persons, event_type):
        """
        Returns the title of the event. The title of the event is a combination
        of the list of main persons and the event type, which you need to
        specify.
        """
        title = ', '.join(filter(None, (event_type, ' & '.join(main_persons))))
        return unicode(title)

    def _get_source_type(self):
        """
        Returns the type of the source of this A2A record.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceType')

    def _get_source_place(self):
        """
        Returns the place of the source.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourcePlace/a2a:Place')

    def _get_description(
            self, institutionName, sourceType, sourcePlace, allPersons):
        """
        Returns a description of the A2A event. This description is constructed
        The description is a concatenation of all persons involved, as well as
        the source type, source place and the name of the institution which
        is the owner of the A2A record.
        """
        return ', '.join(filter(None, (
            institutionName, sourceType, sourcePlace, ' & '.join(allPersons))))

    def _get_date_and_granularity(self):
        """
        Returns the date of the event, or None when it was not available/
        """
        parsed_date = None
        parsed_granularity = 0

        event_date_obj = self._get_node_or_none(
            './/oai:metadata/a2a:A2A/a2a:Event/a2a:EventDate')
        if event_date_obj is not None:
            event_date_day = self._get_text_or_none(
                './a2a:Day', event_date_obj)
            event_date_month = self._get_text_or_none(
                './a2a:Month', event_date_obj)
            event_date_year = self._get_text_or_none(
                './a2a:Year', event_date_obj)
            if event_date_year is not None:
                if (event_date_month is not None and
                        int(event_date_month) > 0 and
                        int(event_date_month) < 13):
                    if (event_date_day is not None and
                            int(event_date_day) > 0 and
                            int(event_date_day) < 32):
                        parsed_date = datetime.strptime(
                            event_date_day + "-" + event_date_month + "-" +
                            event_date_year, '%d-%m-%Y')
                        parsed_granularity = 8
                    else:
                        parsed_date = datetime.strptime(
                            event_date_month + "-" + event_date_year, '%m-%Y')
                        parsed_granularity = 6
                else:
                    parsed_date = datetime.strptime(event_date_year, '%Y')
                    parsed_granularity = 4
        return parsed_date, parsed_granularity

    def _get_media_urls(self):
        """
        Returns the media urls of the A2A record, if avaiable. The media urls
        are the scans of the certificates.
        """
        media_urls = []

        scan_uri_preview = self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceAvailableScans/'
            'a2a:UriPreview')
        if scan_uri_preview is not None:
            media_urls.append({
                'original_url': scan_uri_preview,
                'content_type': 'image/jpeg'})
        else:   # multiple scans?
            scans = self.original_item.findall(
                './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceAvailableScans/'
                'a2a:Scan', namespaces=self.namespaces)
            if scans is None:
                scans = []
            for scan in scans:
                scan_uri_preview = self._get_text_or_none(
                    'a2a:UriPreview', scan)
                if scan_uri_preview is not None:
                    media_urls.append({
                        'original_url': scan_uri_preview,
                        'content_type': 'image/jpeg'})

        return media_urls

    def _get_document_number(self):
        """
        Returns the document number of the A2A record, if available.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:DocumentNumber')

    def _get_book(self):
        """
        Returns the book from which this A2A record was extracted.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:Book')

    def _get_collection(self):
        """
        Returns the collection, which this A2A record is a part of, if
        available
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:Collection')

    def _get_registry_number(self):
        """
        Returns the registry number for this A2A record, if available.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:RegistryNumber')

    def _get_archive_number(self):
        """
        Returns the archive number of this A2A record, if available.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceReference/'
            'a2a:Archive')

    def _get_source_remark(self):
        """
        Returns the source remark for this A2A record, if avaiable.
        """
        return self._get_text_or_none(
            './/oai:metadata/a2a:A2A/a2a:Source/a2a:SourceRemark/'
            'a2a:Value')

    def _get_authors(self):
        """
        Returns the authors of the certificate. Currently not implemented.
        """
        return []

    def get_combined_index_data(self):
        combined_index_data = {}

        event_type = self._get_event_type()

        event_place = self._get_event_place()

        institution_name = self._get_institution_name()

        main_persons, all_persons = self._get_main_persons()

        combined_index_data['title'] = self._get_title(
            main_persons, event_type)

        source_type = self._get_source_type()

        source_place = self._get_source_place()

        description = self._get_description(
            institution_name, source_type, source_place, all_persons)
        if description:
            combined_index_data['description'] = unicode(description)

        parsed_date, parsed_granularity = self._get_date_and_granularity()
        combined_index_data['date'] = parsed_date
        combined_index_data['date_granularity'] = parsed_granularity

        combined_index_data['authors'] = self._get_authors()

        combined_index_data['media_urls'] = self._get_media_urls()

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        text_items.append(self._get_event_type())
        text_items.append(self._get_event_place())
        text_items.append(self._get_source_type())
        text_items.append(self._get_source_place())
        text_items.append(self._get_institution_name())
        text_items.append(self._get_document_number())
        text_items.append(self._get_book())
        text_items.append(self._get_collection())
        text_items.append(self._get_registry_number())
        text_items.append(self._get_archive_number())
        text_items.append(self._get_source_remark())

        persons = self.original_item.findall(
            './/oai:metadata/a2a:A2A/a2a:Person',
            namespaces=self.namespaces
        )
        if persons is None:
            persons = []
        for person in persons:
            person_name = self._get_node_or_none('.//a2a:PersonName', person)
            person_vn = self._get_text_or_none(
                './/a2a:PersonNameFirstName', person_name)
            person_vv = self._get_text_or_none(
                './/a2a:PersonNamePrefixLastName', person_name)
            person_an = self._get_text_or_none(
                './/a2a:PersonNameLastName', person_name)
            text_items.append(
                ' '.join(filter(None, (person_vn, person_vv, person_an))))

        return u' '.join([ti for ti in text_items if ti is not None])
