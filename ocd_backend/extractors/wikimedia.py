from lxml import etree

from ocd_backend.extractors import BaseExtractor, HttpRequestMixin
from ocd_backend.extractors import log


class WikimediaCommonsExtractor(BaseExtractor, HttpRequestMixin):
    """This extractor fetches metadata of 'File' pages in a particular
    Wikimedia Commons category.

    The Wikipedia API is used first to query for File pages in a specific
    category. For each found page, the metadata is retrieved by using the
    `Commons API <http://tools.wmflabs.org/magnus-toolserver/commonsapi.php>`_.
    """

    commons_api_url = 'http://tools.wmflabs.org/magnus-toolserver/commonsapi.php'

    def __init__(self, *args, **kwargs):
        super(WikimediaCommonsExtractor, self).__init__(*args, **kwargs)

        self.base_url = self.source_definition['wikimedia_base_url']
        self.wikimedia_category = self.source_definition['wikimedia_category']

    def wikimedia_api_call(self, params={}):
        """Calls the MediaWiki API and returns the response as a string.

        :type params: dict
        :param params: a dictonary sent as arguments in the query string
        """
        req_params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtype': 'file',
            'cmtitle': self.wikimedia_category,
            'cmlimit': 250,
            'format': 'xml'
        }
        req_params.update(params)

        log.debug('Getting %s (params: %s)' % (self.base_url, params))
        r = self.http_session.get(self.base_url, params=req_params)
        r.raise_for_status()

        return r.content

    def commons_api_call(self, image_name):
        """Use the Wikimedia Commons API to retrieve media metadata from
        Commons as XML. The response is returned as a string.

        :type image_name: str
        :param image_name: the title of the Commons page containing the
                           image (e.g. ``File:Studioportretten.jpg``)
        """
        params = {
            'image': image_name,
            'forcehtml': '',
        }

        log.debug('Getting %s (params: %s)' % (self.commons_api_url, params))
        r = self.http_session.get(self.commons_api_url, params=params)
        r.raise_for_status()

        return r.content

    def get_all_records(self):
        cmcontinue = None

        while True:
            req_params = {}
            if cmcontinue:
                req_params['cmcontinue'] = cmcontinue

            # Get the file pages in the specified Wiki category
            file_pages = etree.fromstring(self.wikimedia_api_call(req_params))

            # Request the metadata of each page
            for file_page in file_pages.findall('.//cm'):
                page_title = file_page.attrib['title']

                page_meta = self.commons_api_call(page_title)
                page_meta_tree = etree.fromstring(page_meta)

                # Skip this page if the response contains errors (the Commons
                # API doesn't return proper HTTP status codes)
                page_meta_error = page_meta_tree.find('.//error')
                if page_meta_error:
                    log.warning('Skipping "%s" because of Commons API error: %s'
                                % (page_title, page_meta_error.text))
                    continue

                yield 'application/xml', page_meta

            try:
                cmcontinue = file_pages.xpath('.//query-continue/categorymembers/@cmcontinue')[0]
            except IndexError:
                cmcontinue = None

            # When cmcontinue is empty or None, we've reached the last page
            if not cmcontinue:
                log.debug('cmcontinue empty, done fetching category pages')
                break

    def run(self):
        for record in self.get_all_records():
            yield record
