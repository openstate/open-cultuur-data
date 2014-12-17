from datetime import datetime
import re

import requests

from ocd_backend.items import BaseItem
from ocd_backend.utils.misc import parse_date


class GemeenteEdeItem(BaseItem):
    def get_original_object_id(self):
        return unicode(self.original_item['Identificatie'])

    def get_original_object_urls(self):
        objnr = unicode(self.get_original_object_id())
        return {
            'html': 'https://commons.wikimedia.org/wiki/File:%s.jpg' % objnr,
        }

    def get_collection(self):
        return u'Gemeentearchief Ede'

    def get_rights(self):
        return unicode(self.original_item['Licentie'])

    def _get_date_and_granularity(self):
        earliest_date = self.original_item.get(
            'Vroegst mogelijke datering', None
        )
        if earliest_date is not None:
            return 12, datetime.fromtimestamp(int(earliest_date))
        else:
            return None, None

    def _get_image_link(self):
        img_page_url = self.original_item["Link naar de afbeelding"]

        resp = requests.get(img_page_url)
        if resp.status_code < 200 or resp.status_code >= 300:
            return None

        # <div class="fullImageLink" id="file">
        # <a href="//upload.wikimedia.org/wikipedia/commons/b/b1/Bijgebouw_van_
        # jachthuis._-_A.B._Wigman_-_GA32573.jpg">
        matches = re.search(
            '<div class=\"fullImageLink\" id=\"file\"><a href=\"([^\"]+)\">',
            resp.text
        )
        print matches
        if matches is not None:
            return u'https:' + unicode(matches.group(1))
        return None

    def get_combined_index_data(self):
        index_data = {}
        index_data['title'] = unicode(
            self.original_item.get('Omschrijving', '')
        )

        gran, date = self._get_date_and_granularity()
        if gran and date:
            index_data['date_granularity'] = gran
            index_data['date'] = date

        desc = self.original_item.get("Beschrijving van de afbeelding", None)
        if desc is not None:
            index_data['description'] = unicode(desc)

        # author is optional
        index_data['authors'] = [
            unicode(self.original_item.get("Auteur", "A.B. Wigman"))
        ]

        # get jpeg images from static host
        img_url = self._get_image_link()
        if img_url is not None:
            index_data['media_urls'] = [
                {
                    'original_url': img_url,
                    'content_type': 'image/jpeg'
                }
            ]
        else:
            index_data['media_urls'] = []

        index_data['all_text'] = self.get_all_text()

        return index_data

    def get_index_data(self):
        index_data = {}
        return index_data

    def get_all_text(self):
        # all text consists of a simple space concatenation of the fields
        fields = [
            'Identificatie', 'Plaatsnaam', 'Archiefnaam',
            'Archiefnummer', 'Auteur van dataset', 'Trefwoord', 'Auteur',
            'Documenttype', 'Omschrijving', 'Beschrijving van de afbeelding',
            'Naam auteursrechthouder'
        ]

        text = u' '.join(
            [unicode(self.original_item.get(f, '')) for f in fields]
        )
        return unicode(text)
