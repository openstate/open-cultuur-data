from lxml import etree

from ocd_backend.extractors import BaseExtractor, HttpRequestMixin

class CentraalMuseumUtrechtExtractor(BaseExtractor, HttpRequestMixin):
    def call(self):
        """Downloads one static XML file"""
        r = self.http_session.get(self.source_definition['file_url'])
        r.raise_for_status()
        return r.content

    def get_all_records(self):
        """Loops through one XML file, yields all records"""
        tree = etree.fromstring(self.call())
        for record in tree.xpath('//adlibXML/recordList/record'):
            yield 'application/xml', etree.tostring(record)

    def run(self):
        for record in self.get_all_records():
            yield record
