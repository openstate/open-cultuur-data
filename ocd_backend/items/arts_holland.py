import re
from datetime import datetime

from ocd_backend.items import BaseItem


class ArtsHollandItem(BaseItem):
    def get_original_object_id(self):
        return self.original_item.get('id')

    def get_original_object_urls(self):
        return {
            'html': 'http://api.artsholland.com/%s' % self.get_original_object_id(),
            'xml': 'http://api.artsholland.com/%s' % self.get_original_object_id()
        }

    def get_rights(self):
        return u'Unknown'

    def get_collection(self):
        return u'Arts Holland'

    def get_combined_index_data(self):
        combined_index_data = {}

        title = self.original_item.get('title')
        combined_index_data['title'] = title

        description = self.original_item.get('description')
	combined_index_data['description'] = description

	combined_index_data['date'] = None
        combined_index_data['date_granularity'] = 14

	combined_index_data['authors'] = []

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []
        text_items.append(self.original_item.get('title'))

        description = self.original_item.get('description')
	text_items.append(description)
        return u' '.join([ti for ti in text_items if ti is not None])
