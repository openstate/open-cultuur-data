import requests

from ocd_backend.extractors import BaseExtractor
from ocd_backend.extractors import log
from ocd_backend.util.misc import parse_oai_response

class OaiExtractor(BaseExtractor):
    metadata_prefix = 'oai_dc'
    namespaces = {'oai': 'http://www.openarchives.org/OAI/2.0/'}

    def __init__(self, *args, **kwargs):
        super(OaiExtractor, self).__init__(*args, **kwargs)

        # Allows overriding of the metadata prefix via the source settings
        if 'oai_metadata_prefix' in self.source_definition:
            self.metadata_prefix = self.source_definition['oai_metadata_prefix']

        self.oai_base_url = self.source_definition['oai_base_url']

    def oai_call(self, params={}):
        """Makes a call to the OAI endpoint and returns the response as
        a string.

        :type params: dict
        :param params: a dictonary sent as arguments in the query string
        """

        log.debug('Getting %s (params: %s)' % (self.oai_base_url, params))
        r = requests.get(self.oai_base_url, params=params)
        r.raise_for_status()

        return r.content

    def get_all_records(self):
        """Retrieves all available OAI records.

        Records are retrieved by first requesting identifiers via the
        ``ListIdentifiers`` verb. For each identifier, the record is
        requested by using the ``GetRecord`` verb.

        :returns: a generator that yields a tuple for each record,
            a tuple consists of the content-type and the content as a string.
        """

        resumption_token = None
        while True:
            req_params = {'verb': 'ListIdentifiers'}
            if resumption_token:
                req_params['resumptionToken'] = resumption_token
            else:
                req_params['metadataPrefix'] = self.metadata_prefix

            resp = self.oai_call(req_params)

            tree = parse_oai_response(resp)
            record_ids = tree.xpath('//oai:header/oai:identifier/text()',
                                    namespaces=self.namespaces)
            for record_id in record_ids:
                record = self.oai_call({
                    'verb': 'GetRecord',
                    'identifier': record_id,
                    'metadataPrefix': self.metadata_prefix
                })
                yield 'application/xml', record

            resumption_token = tree.find('.//oai:resumptionToken',
                                         namespaces=self.namespaces).text

            # According to the OAI spec, we reached the last page of the
            # list if the 'resumptionToken' element is empty
            if not resumption_token:
                log.debug('resumptionToken empty, done fetching list')
                break

    def run(self):
        for record in self.get_all_records():
            yield record
