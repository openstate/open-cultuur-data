from datetime import datetime

from ocd_backend.items import BaseItem

class OpenbeeldenItem(BaseItem):
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'oi': 'http://www.openbeelden.nl/oai/',
        'oai_oi': 'http://www.openbeelden.nl/feeds/oai/',
        'xml': 'http://www.w3.org/XML/1998/namespace'
    }

    media_mime_types = {
        'webm': 'video/webm',
    }

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(xpath_expression, namespaces=self.namespaces)
        if node:
            return node.text.decode('utf8')

        return None

    def get_original_object_id(self):
        return self.original_item.find('.//oai:header/oai:identifier',
                                       namespaces=self.namespaces).text

    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        return {
            'html': 'http://openbeelden.nl/media/%s/' % original_id.split(':')[-1],
            'xml': 'http://openbeelden.nl/feeds/oai/?verb=GetRecord&identifier=%s&metadataPrefix=oai_oi' % original_id
        }

    def get_object_types(self):
        return self.original_item.xpath('.//oi:type/text()',
                                        namespaces=self.namespaces)

    def get_rights(self):
        return u'Creative Commons Attribution-ShareAlike'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self._get_text_or_none('.//oi:title[@xml:lang="nl"]')
        combined_index_data['title'] = title

        description = self._get_text_or_none('.//oi:abstract[@xml:lang="nl"]')
        if description:
            combined_index_data['description'] = description

        date = self._get_text_or_none('.//oi:date')
        if date:
            combined_index_data['date'] = self._get_text_or_none('.//oi:date')
            combined_index_data['date_granularity'] = 8

        authors = self._get_text_or_none('.//oi:attributionName[@xml:lang="nl"]')
        if authors:
            combined_index_data['authors'] = authors

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        return u''
