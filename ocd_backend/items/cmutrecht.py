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
        return unicode(' - '.join([cl.text for cl in self.original_item.iter('collection')]))

    def get_rights(self):

        # rights are defined for the whole collection.
        return unicode(self.source_definition['rights'])

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


        '''
        'title': unicode,
        'description': unicode,     IS BLANK, NO DESCRIPTION
        'date': datetime,
        'date_granularity': int,
        'authors': list,
        'media_urls': list,
        'all_text': unicode
        '''

        # author is optional
        index_data['authors'] = [unicode(c.text) for c in self.original_item.iter('creator')]

        date, gran = self._get_date_and_granularity()
        index_data = {
            'title' : unicode(self.original_item.find('title').text),
            'date' : date,
            'date_granularity' : gran,
        }

        index_data['all_text'] = get_all_text(self)

        return index_data

    def get_index_data(self):

        return {}

    def get_all_text(self):

        fields = 'title', 'creator', 'notes'
        text = ' '.join([self.original_item.find(f).text for f in fields])
        return unicode(text)
