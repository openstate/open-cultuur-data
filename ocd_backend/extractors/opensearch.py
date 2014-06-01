from copy import deepcopy
from time import sleep

from lxml import etree

from ocd_backend.extractors import BaseExtractor, HttpRequestMixin
from ocd_backend.extractors import log


class OpensearchExtractor(BaseExtractor, HttpRequestMixin):
    per_page_count = 100

    def __init__(self, *args, **kwargs):
        super(OpensearchExtractor, self).__init__(*args, **kwargs)

        self.url = self.source_definition['opensearch_url']
        self.query = self.source_definition['opensearch_query']

        # Allows overriding the number of items that is fetched in a
        # single request
        if 'opensearch_per_page_count' in self.source_definition:
            self.per_page_count = self.source_definition['opensearch_per_page_count']

    def opensearch_call(self, params={}):
        """Makes a call to the Opensearch endpoint and returns an XML tree.

        :type params: dict
        :param params: a dictonary sent as arguments in the query string
        :rtype: lxml.etree
        """

        log.debug('Getting %s (params: %s)' % (self.url, params))

        r = self.http_session.get(self.url, params=params)

        # In case a server error is returned (for example, a gateway
        # time-out), we retry the same request for a number of times
        max_retries = 10
        retried = 0
        while r.status_code >= 500 and retried <= max_retries:
            log.warning('Received server error (status %s), retry %s of %s'
                            % (r.status_code, retried + 1, max_retries))

            sleep_s = retried + 1
            log.warning('Sleeping %s second(s) before retrying...' % sleep_s)
            sleep(sleep_s)

            r = self.http_session.get(self.url, params=params)

            retried += 1

        r.raise_for_status()

        return etree.fromstring(r.content)

    def get_all_results(self):
        """Retrieves all available items in a result set.

        :returns: a generator that yields a tuple for each record,
            a tuple consists of the content-type and the content as a string.
        """

        # Perform an initial call to get the total number of results in
        # the result set
        resp = self.opensearch_call({'q': self.query, 'count': 0})

        total_results = int(resp.find('.//channel/opensearch:totalResults',
                                      namespaces=resp.nsmap).text)
        start_index = 1

        while start_index <= total_results:
            resp = self.opensearch_call({
                'q': self.query,
                'count': self.per_page_count,
                'startIndex': start_index
            })

            # Create a copy of the tree without any items
            itemless_tree = deepcopy(resp)
            for item in itemless_tree.xpath('.//channel/item'):
                item.getparent().remove(item)

            # Construct a tree that only includes the item we are iterating over
            for item in resp.xpath('.//channel/item'):
                single_item_tree = deepcopy(itemless_tree)
                single_item_tree.find('./channel').append(item)

                yield 'application/xml', etree.tostring(single_item_tree)

            start_index += self.per_page_count

    def run(self):
        return self.get_all_results()
