from lxml import etree

from ocd_backend.extractors import BaseExtractor, HttpRequestMixin
from ocd_backend.extractors import log


class AdlibExtractor(BaseExtractor, HttpRequestMixin):
    adlib_query = 'all'
    adlib_xmltype = 'unstructured'
    per_page_limit = 50

    def __init__(self, *args, **kwargs):
        super(AdlibExtractor, self).__init__(*args, **kwargs)

        # Allows overriding the executed query ('all' will return all
        # available records)
        if 'adlib_query' in self.source_definition:
            self.adlib_query = self.source_definition['adlib_query']

        # Allows overriding the XML output type that is requested
        if 'adlib_xmltype' in self.source_definition:
            self.adlib_xmltype = self.source_definition['adlib_xmltype']

        # Allows overriding the max. number of items that is fetched in
        # a single request
        if 'adlib_per_page_limit' in self.source_definition:
            self.per_page_limit = self.source_definition['adlib_per_page_limit']

        self.adlib_base_url = self.source_definition['adlib_base_url']
        self.adlib_database = self.source_definition['adlib_database']

    def adlib_search_call(self, params={}):
        """Makes a call to the Adlib endpoint and returns the response
        as a string.

        :type params: dict
        :param params: a dictonary sent as arguments in the query string
        :rtype: lxml.etree
        """
        default_params = {
            'database': self.adlib_database,
            'search': self.adlib_query,
            'xmltype': self.adlib_xmltype,
            'limit': self.per_page_limit,
            'startfrom': 0
        }

        default_params.update(params)

        log.debug('Getting %s (params: %s)' % (self.adlib_base_url, default_params))
        r = self.http_session.get(
            self.adlib_base_url,
            params=default_params
        )
        r.raise_for_status()

        return etree.fromstring(r.content)

    def get_all_records(self):
        total_hits = 0
        processed_items = 0
        start_from = 1

        while True:
            tree = self.adlib_search_call(params={'startfrom': start_from})

            if not total_hits:
                total_hits = int(tree.find('.//diagnostic/hits').text)

            for record in tree.xpath('.//recordList//record'):
                processed_items += 1
                yield 'application/xml', etree.tostring(record)

            start_from += self.per_page_limit

            if processed_items == total_hits:
                break

    def run(self):
        for record in self.get_all_records():
            yield record
