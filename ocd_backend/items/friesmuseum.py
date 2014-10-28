import datetime

from ocd_backend.items import BaseItem
from ocd_backend.utils.misc import parse_date


class FriesMuseumItem(BaseItem):
    # Granularities
    regexen = [
        # Dates are noise-free!
        ('\?$', (0, lambda _ : None)),
        ('(\d\d\d0)[\?() ]+$', (3, lambda (y,): datetime.datetime(int(y), 1, 1))),
        ('(\d+)$', (4, lambda (y,): datetime.datetime(int(y), 1, 1))),
        ('(\d\d\d\d)-(\d+)$', (6, lambda (y, m): datetime.datetime(int(y), int(m), 1))),
        ('(\d\d\d\d)-(\d+)-(\d+)$', (8, lambda (y,m,d) : datetime.datetime(int(y), int(m), int(d))) ),
    ]

    def get_original_object_id(self):
        return unicode(self.original_item.find('object_number').text)

    def get_original_object_urls(self):
        objnr = unicode(self.original_item.find('object_number').text)
        return {
            'html': 'http://friesmuseum.delving.org/friesmuseum/fries-museum/%s' % objnr,
        }

    def get_collection(self):
        return u'Fries Museum'

    def get_rights(self):
        # rights are defined for the whole collection.
        return u'No Rights Reserved / Public Domain'

    def _get_date_and_granularity(self):
        if self.original_item.find('production.date.start') is not None:
            pds_text = self.original_item.find('production.date.start').text
            # always take the production start date. period does not matter.
            return parse_date(self.regexen, pds_text)
        else:
            return None, None

    def get_combined_index_data(self):
        index_data = {}
        if self.original_item.find('title') is not None:
            index_data['title'] = unicode(self.original_item.find('title').text)

        gran, date = self._get_date_and_granularity()
        if gran and date:
            index_data['date_granularity'] = gran
            index_data['date'] = date

        if self.original_item.find('label.text') is not None:
            index_data['description'] = unicode(self.original_item.find('label.text').text)

        # author is optional
        index_data['authors'] = [unicode(c.text) for c in self.original_item.iter('creator')]

        # get jpeg images from static host
        img_url = 'http://static.opencultuurdata.nl/fries_museum/%s.jpg'
        files = [c.text for c in self.original_item.iter('reproduction.reference') if c.text]
        index_data['media_urls'] = [
                {
                    'original_url': img_url % fname,
                    'content_type': 'image/jpeg'
                }
            for fname in files]

        return index_data

    def get_index_data(self):
        index_data = {}

        # measurements
        fields = ['type', 'value', 'unit']
        dim = zip(*[[c.text for c in self.original_item.iter('dimension.'+f)]
                    for f in fields])
        index_data['measurements'] = [
            {
                'type': t,
                'value': v.replace(',','.'),
                'unit': u
            }
            for (t, v, u) in dim if t and v and v not in ['?', '...', '....']]

        # acquisition
        fields = ['date', 'method']
        aq = zip(*[[c.text for c in self.original_item.iter('acquisition.'+f)]
                   for f in fields])
        aq = [
            {
                'date' : d,
                'date_granularity' : g,
                'method' : m
            }
            for (ds,m) in aq if ds or m for g,d in [parse_date(self.regexen, ds)]]
        index_data['acquisition'] = aq[0] if aq else None  # singleton

        # listed attributes
        attrs = {
            'collection': 'collections',
            'material': 'materials',
            'production.place': 'production_place',
            'technique': 'technique',
            'object_name': 'tags',
        }
        for attr, index_name in attrs.items():
            val = [unicode(c.text) for c in self.original_item.iter(attr) if c.text]
            if val:
                index_data[index_name] = val

        if 'production_place' in index_data: # singleton
            index_data['production_place'] = index_data['production_place'][0]

        return index_data

    def get_all_text(self):
        # all text consists of a simple space concatenation of the fields
        fields = ['title', 'creator', 'production.place', 'collection',
                  'object_name', 'technique', 'material']

        text = ' '.join([unicode(c.text) for f in fields for c in
                         self.original_item.iter(f) if c.text])
        return unicode(text)
