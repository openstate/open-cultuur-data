from lxml import etree

from ocd_backend.extractors import BaseExtractor, HttpRequestMixin
from ocd_backend.extractors import log


class CommonsExtractor(BaseExtractor, HttpRequestMixin):
    def __init__(self, *args, **kwargs):
        super(CommonsExtractor, self).__init__(*args, **kwargs)

        self.base_url = self.source_definition['wikimedia_base_url']
        self.wikimedia_title = self.source_definition['wikimedia_title']

    def wikimedia_api_call(self, params={}):
        """Makes a call to the OAI endpoint and returns the response as
        a string.

        :type params: dict
        :param params: a dictonary sent as arguments in the query string
        """

        log.debug('Getting %s (params: %s)' % (self.base_url, params))
        r = self.http_session.get(self.base_url, params=params)
        r.raise_for_status()

        return r.content

    def get_images_in_category(self, cat_name, other_params={}):
        default_params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtype': 'file',
            'cmtitle': cat_name,
            'format': 'xml'
        }
        default_params.update(other_params)
        return self.wikimedia_api_call(params=default_params)

    def get_image_info(self, image_file):
        commons_api_base_url = 'http://tools.wmflabs.org/magnus-toolserver/commonsapi.php'
        # http://tools.wmflabs.org/magnus-toolserver/commonsapi.php?image=Sa-warthog.jpg&thumbwidth=150&thumbheight=150&versions&meta
        params = {
            'image': image_file,
            'thumbwidth': 150,
            'thumbheight': 150,
            'versions': '',
            'meta': ''
        }

        log.debug('Getting %s (params: %s)' % (commons_api_base_url, params))
        r = self.http_session.get(commons_api_base_url, params=params)
        r.raise_for_status()

        return r.content



    def parse_wikimedia_response(self, content):
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

    def get_record(self, record):
        image_file = record.attrib['title'].replace('File:', '')
        content = self.get_image_info(image_file)
        print content
        return content

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
            req_params = {}
            if resumption_token:
                req_params['cmcontinue'] = resumption_token

            resp = self.get_images_in_category(self.wikimedia_title, req_params)
            tree = self.parse_wikimedia_response(resp)

            records = tree.xpath(
                './/cm'
            )

            for record in records:
                yield 'application/xml', self.get_record(record)

            try:
                resumption_token = tree.xpath('.//@cmcontinue')[0]
            except IndexError, e:
                resumption_token = None
            except AttributeError, e:
                resumption_token = None

            # According to the OAI spec, we reached the last page of the
            # list if the 'resumptionToken' element is empty
            if not resumption_token:
                log.debug('resumptionToken empty, done fetching list')
                break

    def run(self):
        for record in self.get_all_records():
            yield record
