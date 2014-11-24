from datetime import datetime
from pprint import pprint

from ocd_backend.items import BaseItem


class GAZaanstadItem(BaseItem):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcterms': 'http://purl.org/dc/terms/',
        'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'europeana': 'http://www.europeana.eu/schemas/ese/',
        'xml': 'http://www.w3.org/XML/1998/namespace'
    }

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(
            xpath_expression, namespaces=self.namespaces
        )
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def get_original_object_id(self):
        return self._get_text_or_none('.//oai:header/oai:identifier')

    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        return {
            'html': self._get_text_or_none(
                './/oai:metadata/europeana:record/europeana:isShownAt'
            ),
            'xml': ('https://maior.memorix.nl/api/oai/zaa/key/'
                    '3e1f051a-62df-492b-a060-c001e4db644f/?verb=GetRecord'
                    '&identifier=%s&metadataPrefix=ese') % original_id
        }

    def get_collection(self):
        return u'Gemeentearchief Zaanstad'

    def get_rights(self):
        return u'Creative Commons 0'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//dc:title')
        combined_index_data['title'] = title

        description = self._get_text_or_none('.//dc:description')
        if description:
            combined_index_data['description'] = description

        date = self._get_text_or_none('.//dcterms:created')
        if date:
            combined_index_data['date'] = datetime.strptime(
                date, '%Y'
            )
            combined_index_data['date_granularity'] = 4

        authors = self._get_text_or_none('.//dc:creator')
        if authors:
            combined_index_data['authors'] = [authors]

        mediums = self.original_item.findall(
            './/europeana:isShownBy', namespaces=self.namespaces
        )  # always jpg

        combined_index_data['media_urls'] = []
        if mediums is not None:
            combined_index_data['media_urls'] = [
                {'original_url': medium.text, 'content_type': 'image/jpg'}
                for medium in mediums
            ]

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []

        # Title
        text_items.append(self._get_text_or_none('.//dc:title'))

        # Creator
        text_items.append(self._get_text_or_none('.//dc:creator'))

        # Subject
        subjects = self.original_item.findall('.//dcterms:spatial',
                                              namespaces=self.namespaces)
        for subject in subjects:
            text_items.append(unicode(subject.text))

        # Description
        text_items.append(self._get_text_or_none('.//dc:description'))

        # Publisher
        text_items.append(self._get_text_or_none('.//europeana:provider'))

        # Identifier
        text_items.append(self._get_text_or_none('.//dc:identifier'))

        # Type
        text_items.append(self._get_text_or_none('.//dc:type'))

        return u' '.join([ti for ti in text_items if ti is not None])
