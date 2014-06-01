from ocd_backend.items import BaseItem
import datetime
from ocd_backend.utils.misc import try_convert


class CentraalMuseumUtrechtItem(BaseItem):

    # itemclass for centraal museum utrecht
    # author :  Gijs Koot - gijs.koot@tno.nl

    def get_original_object_id(self):
        return unicode(self.original_item.find('object_number').text)

    def get_original_object_urls(self):

        # there is no original object url, it is retrieved from an xml
        return {}

    def get_collection(self):

        # there are multiple collections in this case. returning a join by dashes of the collections
        # would be return unicode(' - '.join([cl.text for cl in self.original_item.iter('collection')]))

        # but
        return u'Centraal Museum Utrecht'

    def get_rights(self):

        # rights are defined for the whole collection.
        return u'No Rights Reserved / Public Domain'

    def _get_date_and_granularity(self):

        # returns rule based date and granularity based on internal fields

        # TODO: day-dates, absence

        # if there is no production.date.start, we crash
        pds = int(self.original_item.find('production.date.start').text) 
        gran = 2 # default granularity is two
        if self.original_item.find('production.date.end'):
            pde = int(self.original_item.find('production.date.end').text)
            if pde - pds < 50 : gran = 3
            if pde - pds < 5 : gran = 4

        return datetime.datetime(pds, 1, 1), gran

    def get_combined_index_data(self):

        date, gran = self._get_date_and_granularity()
        index_date = dict()
        index_data = {
            'title' : unicode(self.original_item.find('title').text),
            'date' : date,
            'date_granularity' : gran,
        }

        # index_data['all_text'] = self.get_all_text()
        if self.original_item.find('notes'):
            index_data['description'] = unicode(self.original_item.find('notes').text)
        if self.original_item.find('label.text') and self.original_item.find('label.text').text:
            index_data['description'] = unicode(self.original_item.find('label.text').text)

        # author is optional
        index_data['authors'] = [unicode(c.text) for c in self.original_item.iter('creator')]

        # get jpeg images from static host
        img_url = 'http://cmu.adlibhosting.com/wwwopacximages/wwwopac.ashx?command=getcontent&server=images&value=%s&width=500&height=500'
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
                'value' : try_convert(float, v), 
                'unit' : u
            }
            for (t,v,u) in dim if t and v and v not in ['?','...','....']]

        # acquisition
        index_data['acquisition'] = {}
        method = self.original_item.find('acquisition.method')
        if method and method.text:
            index_data['acquisition']['method'] = unicode(method.text)
        date = self.original_item.find('acquisition.date')
        if date and date.text and date.text not in ['?', '??', '?? +', 'onbekend', 'onbekend +']:
            # TODO: parse date & granularity
            index_data['acquisition']['date'] = unicode(date.text)
            index_data['acquisition']['date_granularity'] = None

        # collections
        index_data['collections'] = [unicode(c.text) for c in self.original_item.iter('collection') if c.text]

        # creators
        fields = ['creator', 'creator.role']
        # creator.qualifier is never defined
        roles = [[c.text for c in self.original_item.iter(f) if c.text] for f in fields]
        if all(roles):
            index_data['creator_roles'] = dict(zip(*roles))

        # materials
        materials = [c.text for c in self.original_item.iter('material') if c.text]
        if materials:
            index_data['materials'] = materials

        # tags
        tags = [c.text for c in self.original_item.iter('object_name') if c.text]
        if tags:
            index_data['tags'] = tags

        # technique
        technique = [c.text for c in self.original_item.iter('techniek.vrije.tekst') if c.text]
        if technique:
            index_data['technique'] = technique

        return index_data

    def get_all_text(self):

        # all text consists of a simple space concatenation of the fields
        fields = 'title', 'creator', 'notes', 'collection'
        text = ' '.join([self.original_item.find(f).text for f in fields if not self.original_item.find(f) is None])
        return unicode(text)
