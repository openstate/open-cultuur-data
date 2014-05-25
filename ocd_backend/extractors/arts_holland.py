from copy import deepcopy
from time import sleep

from lxml import etree
import requests
import unittest
import json

from ocd_backend.extractors import BaseExtractor
from ocd_backend.extractors import log
import logging

class ArtsHollandExtractor(BaseExtractor):
    limit = 100

    def __init__(self, *args, **kwargs):
        super(ArtsHollandExtractor, self).__init__(*args, **kwargs)

        self.url = self.source_definition['url']

        # Allows overriding the number of items that is fetched in a
        # single request
        if 'limit' in self.source_definition:
            self.limit = self.source_definition['limit']

    def call(self, url, headers, data):
        log.debug('Getting %s (headers: %s, data: %s)' % (self.url, headers, data))

	r = requests.post(self.url, data=data, headers=headers)

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

	    r = requests.post(url, data=data, headers=headers)

            retried += 1

        r.raise_for_status()

        return r.json()

    def get_item(self, url):
	query = """
		SELECT DISTINCT ?property ?hasValue ?isValueOf
		WHERE {{
			{{ <{0}> ?property ?hasValue }}
			UNION
			{{ ?isValueOf ?property <{0}> }}
		}}
		ORDER BY (!BOUND(?hasValue)) ?property ?hasValue ?isValueOf
		"""

	headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/sparql-results+json'}
	result = self.call(self.url, data={'query': query.format(url)}, headers=headers)

	binding = result.get('results').get('bindings')
	return (json.dumps(binding))

    def get_all_results(self):
        """Retrieves all available items in a result set.

        :returns: a generator that yields a tuple for each record,
            a tuple consists of the content-type and the content as a string.
        """

	query = """
		SELECT DISTINCT ?instance
		WHERE {{
		    ?instance a <http://purl.org/artsholland/1.0/Production>
		    }} ORDER BY ?instance
		    OFFSET {0} LIMIT {1}
	"""

	headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/sparql-results+json'}

	offset = 0

	while True:
		result = self.call(self.url, data={'query': query.format(offset, self.limit)}, headers=headers)

		if len(result.get('results').get('bindings'))==0:
			break

		for binding in result.get('results').get('bindings'):
			url = binding.get('instance').get('value')
			item = self.get_item(url)
			yield 'application/json', item

		offset = offset + len(result.get('results').get('bindings'))


    def run(self):
        return self.get_all_results()


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_download_results(self):
	extractor = ArtsHollandExtractor({ 'url': 'http://api.artsholland.com/sparql' })            
	for result in extractor.get_all_results():
		log.debug ("result %s %s", result[0], result[1])
		pass
	
	
if __name__ == "__main__":
    unittest.main()


