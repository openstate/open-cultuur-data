from datetime import datetime

from ocd_backend.items import BaseItem

class CentraalMuseumUtrechtItem(BaseItem):

    def _get_text_or_none(self, xpath_expression):
        node = self.original_item.find(xpath_expression)
        if node is not None and node.text is not None:
            return unicode(node.text)

        return None

    def get_original_object_id(self):
        return self._get_text_or_none('priref')

    def get_original_object_urls(self):
        return {}

    def get_rights(self):
        return u'DUMMY LICENCE'

    def get_collection(self):
        return u'Centraal Museum Utrecht'

    def get_combined_index_data(self):

        combined_index_data = {}

        fields = {
            'title': 'title',
            'description': 'notes'
        }
        for field, xpath in fields.items():
            combined_index_data[field] = self._get_text_or_none(xpath)

        return combined_index_data

    def get_all_text(self):
        text_items = []
    
        return u' '.join(text_items)

    def get_index_data(self):
        return {}
        