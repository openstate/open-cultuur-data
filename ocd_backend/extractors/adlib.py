from lxml import etree

from ocd_backend.extractors import BaseExtractor, HttpRequestMixin
from ocd_backend.extractors import log


class AdlibExtractor(BaseExtractor, HttpRequestMixin):
    metadata_prefix = 'oai_dc'
    oai_set = ''
    namespaces = {'oai': 'http://www.openarchives.org/OAI/2.0/'}

    def __init__(self, *args, **kwargs):
        super(AdlibExtractor, self).__init__(*args, **kwargs)

        for prop in ["base_url", "database", "xmltype", "limit", "search"]:
            full_prop = "adlib_%s" % prop
            if full_prop in self.source_definition:
                setattr(self, full_prop, self.source_definition[full_prop])

    def adlib_search_call(self, params={}):
        """Makes a call to the Adlib endpoint and returns the response as
        a string.

        :type params: dict
        :param params: a dictonary sent as arguments in the query string
        """

        search_url = self.adlib_base_url

        default_params = {
            'database': self.adlib_database,
            'search': self.adlib_search,
            'xmltype': self.adlib_xmltype,
            'limit': self.adlib_limit,
            'startfrom': 0
        }
        default_params.update(params)

        log.debug('Getting %s (params: %s)' % (search_url, default_params))
        r = self.http_session.get(
            search_url,
            params=default_params
        )
        r.raise_for_status()

        return r.content

    def parse_adlib_response(self, content):
        """Parses an Adlib XML response and returns an XML tree.

        The input source is expected to be in UTF-8. To get around
        well-formedness errors (which occur in many responses), bad
        characters are ignored.

        :param content: the Adlib XML response as a string.
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

        Records are retrieved by first requesting identifiers via the
        ``ListIdentifiers`` verb. For each identifier, the record is
        requested by using the ``GetRecord`` verb.

        :returns: a generator that yields a tuple for each record,
            a tuple consists of the content-type and the content as a string.
        """
        resumption_token = 0
        while True:
            req_params = {}
            if resumption_token:
                req_params['startfrom'] = resumption_token

            resp = self.adlib_search_call(params=req_params)
            tree = self.parse_adlib_response(resp)

            records = tree.xpath('.//recordList//record',
                                 namespaces=self.namespaces)
            for record in records:
                yield 'application/xml', etree.tostring(record)

            try:
                hits = int(tree.xpath('.//diagnostic/hits/text()')[0])
            except IndexError, e:
                hits = 0
            except TypeError, e:
                hits = 0

            log.debug('Got %s hits on the search from Adlib' % hits)

            resumption_token += self.adlib_limit
            if resumption_token >= hits:
                log.debug('resumptionToken empty, done fetching list')
                break

    def run(self):
        for record in self.get_all_records():
            yield record
