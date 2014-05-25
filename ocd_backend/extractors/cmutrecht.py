from lxml import etree

import requests

from ocd_backend.extractors import BaseExtractor
from ocd_backend.extractors import log
from ocd_backend.exceptions import NotFound

class CentraalMuseumUtrechtExtractor(BaseExtractor):

    def call(self):
        """
        Downloads one static XML file
        """
        r = requests.get(self.source_definition['file_url'])
        r.raise_for_status()
        return r.content

    def get_all_records(self):
        """
        Loops through one XML file, yields all records
        """
        result = self.call()
        parser = etree.XMLParser(recover=True, encoding='utf-8')
        tree = etree.fromstring(result.encode('utf-8'), parser=parser)
        for record in tree.xpath('//adlibXML/recordList/record'):
            yield 'application/xml', etree.tostring(record)

    def run(self):
        for record in self.get_all_records():
            yield record