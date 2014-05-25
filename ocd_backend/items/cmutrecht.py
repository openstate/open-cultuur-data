from ocd_backend.items import BaseItem
import datetime

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
        pds = int(self.original_item.find('production.date.start').text) # if there is no production.date.start, we crash
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

        index_data['all_text'] = self.get_all_text()

        # author is optional
        index_data['authors'] = [unicode(c.text) for c in self.original_item.iter('creator')]


        return index_data

    def get_index_data(self):

        return {}

    def get_all_text(self):

        # all text consists of a simple space concatenation of the fields
        fields = 'title', 'creator', 'notes'
        text = ' '.join([self.original_item.find(f).text for f in fields if not self.original_item.find(f) is None])
        return unicode(text)
