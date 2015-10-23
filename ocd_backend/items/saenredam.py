from datetime import datetime
import re
from pprint import pprint

import requests

from ocd_backend.items import BaseItem
from ocd_backend.utils.misc import parse_date
from ocd_backend.extractors import HttpRequestMixin


class SaenredamItem(BaseItem, HttpRequestMixin):
    def get_original_object_id(self):
        return unicode(self.original_item['Identificatie'])

    def get_original_object_urls(self):
        return {
            'html': (
                u'http://www.hetutrechtsarchief.nl/collectie/beeldmateriaal/'
                u'tekeningen_en_prenten/1400-1410/%s') %
                (self.original_item['Identificatie'],),
        }

    def get_collection(self):
        return u'Het Utrechts Archief - Saenredam Collectie'

    def get_rights(self):
        return unicode(self.original_item['Licentie']) + u'deed.nl'

    def _get_date_and_granularity(self):
        earliest_date = self.original_item.get(
            'Vroegst mogelijke datering', None)
        if earliest_date is not None:
            parts = earliest_date.split('/', 2)
            return 8, datetime(int(parts[2]), int(parts[1]), int(parts[0]))
        else:
            return 16, None

    def _get_image_link(self):
        return u'%s%s-%s.jpg' % (
            self.source_definition['media_base_url'],
            self.original_item['Nummer'].replace(' ', ''),
            self.original_item['Identificatie'],)

    def get_combined_index_data(self):
        index_data = {}

        if self.original_item['Trefwoord'] != '':
            index_data['title'] = unicode(self.original_item.get('Trefwoord'))

        gran, date = self._get_date_and_granularity()
        index_data['date_granularity'] = gran
        index_data['date'] = date

        desc = self.original_item.get("Beschrijving van de voorstelling", '')
        if desc != '':
            index_data['description'] = unicode(desc)

        # author is optional
        index_data['authors'] = [unicode(self.original_item["Auteur"])]

        # get jpeg images from static host
        index_data['media_urls'] = []
        img_url = self._get_image_link()
        if img_url is not None:
            result = self.http_session.head(img_url)
            if result.status_code == 200:
                index_data['media_urls'] = [{
                    'original_url': img_url,
                    'content_type': 'image/jpeg'}]

        index_data['all_text'] = self.get_all_text()

        return index_data

    def get_index_data(self):
        index_data = {}
        return index_data

    def get_all_text(self):
        # all text consists of a simple space concatenation of the fields
        fields = ['Collectie', 'Nummer', 'Plaats', 'Trefwoord', 'Auteur',
            'Identificatie', 'Beschrijving van de voorstelling', 'Titel']

        text = u' '.join(
            [unicode(self.original_item.get(f, '')) for f in fields])

        return unicode(text.strip())
