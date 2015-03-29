from lxml import etree

from ocd_backend.extractors import BaseExtractor, HttpRequestMixin
from ocd_backend.extractors import log


class OaiExtractor(BaseExtractor, HttpRequestMixin):
    metadata_prefix = 'oai_dc'
    oai_set = ''
    namespaces = {'oai': 'http://www.openarchives.org/OAI/2.0/'}

    def __init__(self, *args, **kwargs):
        super(OaiExtractor, self).__init__(*args, **kwargs)

        # Allows overriding of the metadata prefix via the source settings
        if 'oai_metadata_prefix' in self.source_definition:
            self.metadata_prefix = self.source_definition['oai_metadata_prefix']

        # Allows selecting a specific set (or collection)
        if 'oai_set' in self.source_definition:
            self.oai_set = self.source_definition['oai_set']

        self.oai_base_url = self.source_definition['oai_base_url']

    def oai_call(self, params={}):
        """Makes a call to the OAI endpoint and returns the response as
        a string.

        :type params: dict
        :param params: a dictonary sent as arguments in the query string
        """
        # Add the set variable to the parameters (if available)
        if self.oai_set:
            params['set'] = self.oai_set

        # Remove set and metadataPrefix, when a resumptionToken is present
        if 'resumptionToken' in params:
            if 'set' in params:
                del params['set']

        log.debug('Getting %s (params: %s)' % (self.oai_base_url, params))
        r = self.http_session.get(self.oai_base_url, params=params)
        r.raise_for_status()

        return r.content

    def parse_oai_response(self, content):
        """Parses an OAI XML response and returns an XML tree.

        The input source is expected to be in UTF-8. To get around
        well-formedness errors (which occur in many responses), bad
        characters are ignored.

        :param content: the OAI XML response as a string.
        :type content: string
        :rtype: lxml.etree._Element
        """
        content = unicode(content, 'UTF-8', 'replace')
        # get rid of character code 12 (form feed)
        content = content.replace(chr(12), '?')

        parser = etree.XMLParser(recover=True, encoding='utf-8')

        return etree.fromstring(content.encode('utf-8'), parser=parser)

    def get_all_records(self):
        """Retrieves all available OAI records.

        :returns: a generator that yields a tuple for each record,
            a tuple consists of the content-type and the content as a string.
        """
        resumption_token = None
        while True:
            req_params = {'verb': 'ListRecords'}
            if resumption_token:
                req_params['resumptionToken'] = resumption_token

            req_params['metadataPrefix'] = self.metadata_prefix

            resp = self.oai_call(req_params)
            tree = self.parse_oai_response(resp)

            records = tree.xpath('.//oai:ListRecords/oai:record',
                                 namespaces=self.namespaces)
            for record in records:
                # check if the record was deleted
                header = record.find('oai:header[@status="deleted"]',
                                     namespaces=self.namespaces)
                if header is not None:
                    log.debug('Header specifies that the record is deleted, skipping.')
                    continue

                yield 'application/xml', etree.tostring(record)


            # According to the OAI spec, we reached the last page of the
            # list if the 'resumptionToken' element is empty. Some OAI
            # implementations completely drop the 'resumptionToken'
            # element on the last
            try:
                resumption_token = tree.find('.//oai:resumptionToken',
                                             namespaces=self.namespaces).text
            except AttributeError:
                resumption_token = None

            if not resumption_token:
                log.debug('resumptionToken empty, done fetching list')
                break

    def run(self):
        for record in self.get_all_records():
            yield record
