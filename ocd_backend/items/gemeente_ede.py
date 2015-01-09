import datetime

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
        return u'Gemeente Ede'

    def get_rights(self):
        return unicode(self.original_item['Licentie'])

    def _get_date_and_granularity(self):
        earliest_date = self.original_item.get(
            'Vroegst mogelijke datering', None
        )
        if earliest_date is not None:
            return 12, datetime.datetime.fromtimestamp(int(earliest_date))
        else:
            return None, None

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
        img_url = self.original_item["Link naar de afbeelding"]
        index_data['media_urls'] = [
            {
                'original_url': img_url,
                'content_type': 'image/jpeg'
            }
        ]

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
