from ocd_backend.items import BaseItem
import datetime
from ocd_backend.utils.misc import try_convert, parse_date, parse_date_span

class CentraalMuseumUtrechtItem(BaseItem):
    # Granularities
    regexen = [
        ('\?$', (0, lambda _ : None) ),
        ('(\d\d)[\?]+$', (2, lambda (y,) : datetime.datetime(int(y+'00'), 1, 1)) ),
        ('(\d\d\d)\?$', (3, lambda (y,) : datetime.datetime(int(y+'0'), 1, 1)) ),
        ('(\d\d\d\d) ?- ?\d\d\d\d$', (3, lambda (y,) : datetime.datetime(int(y), 1, 1)) ),
        ('(\d\d\d0)[\?() ]+$', (3, lambda (y,) : datetime.datetime(int(y), 1, 1)) ),
        # 'yyyy?' will still have a date granularity of 4
        ('(\d\d\d\d)[\?() ]+$', (4, lambda (y,) : datetime.datetime(int(y), 1, 1)) ),
        ('(\d+)$', (4, lambda (y,) : datetime.datetime(int(y), 1, 1)) ),
        ('(\d\d\d\d)-(\d+)$', (6, lambda (y,m) : datetime.datetime(int(y), int(m), 1)) ),
        ('(\d\d\d\d)-(\d+)-(\d+)$', (8, lambda (y,m,d) : datetime.datetime(int(y), int(m), int(d))) ),
    ]

    def get_original_object_id(self):
        return unicode(self.original_item.find('object_number').text)

    def get_original_object_urls(self):
        priref = unicode(self.original_item.find('priref').text)
        return {
            'html': 'http://centraalmuseum.nl/ontdekken/object/%s' % priref,
        }

    def get_collection(self):
        return u'Centraal Museum Utrecht'

    def get_rights(self):
        # rights are defined for the whole collection.
        return u'No Rights Reserved / Public Domain'

    def _get_date_and_granularity(self):
        if self.original_item.find('production.date.start') is not None:
            pds_text = self.original_item.find('production.date.start').text
            #pde_text = self.original_item.find('production.date.end').text

            #return parse_date_span(self.regexen, pds_text, pde_text)
            # always take the production start date. period does not matter.
            return parse_date(self.regexen, pds_text)
        else:
            return None, None

    def get_combined_index_data(self):
        index_data = {}
        if self.original_item.find('title') != None:
            index_data['title'] = unicode(self.original_item.find('title').text)

        gran, date = self._get_date_and_granularity()
        if gran and date:
            index_data['date_granularity'] = gran
            index_data['date'] = date

        if self.original_item.find('label.text') != None:
            index_data['description'] = unicode(self.original_item.find('label.text').text)

        # author is optional
        index_data['authors'] = [unicode(c.text) for c in self.original_item.iter('creator')]

        # get jpeg images from static host
        img_url = 'http://cmu.adlibhosting.com/wwwopacximages/wwwopac.ashx?command=getcontent&server=images&value=%s'
        files = [c.text for c in self.original_item.iter('reproduction.identifier_URL') if c.text]
        index_data['media_urls'] = [
                {
                    'original_url': img_url % fname,
                    'content_type': 'image/jpeg'
                }
            for fname in files if fname[-3:].lower() == 'jpg']

        return index_data

    def get_index_data(self):
        index_data = {}

        # measurements
        fields = ['type', 'value', 'unit']
        dim = zip(*[[c.text for c in self.original_item.iter('dimension.'+f)] for f in fields])
        index_data['measurements'] = [
            {
                'type' : t,
                'value' : v.replace(',','.'),
                'unit' : u
            }
            for (t,v,u) in dim if t and v and v not in ['?','...','....']]

        # acquisition
        date = self.original_item.find('acquisition.date')
        method = self.original_item.find('acquisition.method')
        g,d = 0, None
        if not method == None and method.text:
            method = method.text
        if not date == None and date.text:
            date = date.text.replace("+","").strip() # the meaning of '+' is unknown
            if date not in ['?', '??', 'onbekend']:
                g,d = parse_date(self.regexen, date)
        index_data['acquisition'] = {
            'method' : method,
            'date' : d,
            'date_granularity' : g
        }

        # creator roles
        fields = ['creator', 'creator.role']
        # creator.qualifier is never defined
        roles = [[c.text for c in self.original_item.iter(f) if c.text] for f in fields]
        if all(roles):
            index_data['creator_roles'] = [
                {
                    'creator' : r[0],
                    'role' : r[1]
                }
                for r in zip(*roles)]

        # listed attributes
        attrs = {
            'collections' : 'collections',
            'material' : 'materials',
            'object_name' : 'tags',
            'techniek.vrije.tekst' : 'technique',
            'notes' : 'notes',
        }
        for attr, index_name in attrs.items():
            val = [unicode(c.text) for c in self.original_item.iter(attr) if c.text]
            if val:
                index_data[index_name] = val

        return index_data

    def get_all_text(self):
        # all text consists of a simple space concatenation of the fields
        fields = ['title', 'creator', 'notes', 'collection', 'object_name',
                  'techniek.vrije.tekst', 'material']

        text = ' '.join([unicode(c.text) for f in fields for c in self.original_item.iter(f) if c.text])
        return unicode(text)
