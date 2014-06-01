from math import ceil
import json

from ocd_backend.extractors import BaseExtractor, HttpRequestMixin
from ocd_backend.extractors import log
from ocd_backend.exceptions import NotFound


class RijksmuseumExtractor(BaseExtractor, HttpRequestMixin):
    api_base_url = 'https://www.rijksmuseum.nl/api/nl/'
    items_per_page = 100 # The number of items to request in a single API call

    def api_call(self, url, params={}):
        params.update(key=self.source_definition['rijksmuseum_api_key'],
                      format='json')
        url = '%s%s' % (self.api_base_url, url)

        log.debug('Getting %s (params: %s)' % (url, params))
        r = self.http_session.get(url, params=params)
        r.raise_for_status()

        return r.json()

    def get_collection_objects(self):
        # Perform an initial call to get the total number of results
        resp = self.api_call('collection/', params={'p': 0, 'ps': 1})
        total_items = resp['count']

        # Calculate the total number of pages that are available
        total_pages = int(ceil(total_items / float(self.items_per_page)))

        log.info('Total collection items to fetch %s (%s pages)', total_items, total_pages)

        for p in xrange(0, total_pages):
            log.info('Getting collection items page %s of %s', p, total_pages)
            resp = self.api_call('collection/', params={
                'p': p,
                'ps': self.items_per_page
            })

            for item in resp['artObjects']:
                yield item

    def get_object(self, object_number):
        log.info('Getting object: %s', object_number)

        resp = self.api_call('collection/%s' % object_number)
        if not resp['artObject']:
            raise NotFound

        return 'application/json', json.dumps(resp['artObject'])

    def run(self):
        if ('rijksmuseum_api_key' not in self.source_definition or not
                self.source_definition['rijksmuseum_api_key']):
            raise ValueError('Missing Rijksmuseum API key in source settings')

        for item in self.get_collection_objects():
            yield self.get_object(item['objectNumber'])
