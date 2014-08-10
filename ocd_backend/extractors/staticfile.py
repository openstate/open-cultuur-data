from ocd_backend.extractors import BaseExtractor, HttpRequestMixin
from ocd_backend.exceptions import ConfigurationError

from lxml import etree


class StaticFileBaseExtractor(BaseExtractor, HttpRequestMixin):
    """ A base class for implementing extractors that retrieve items
    by fetching a single statically hosted external file."""

    def __init__(self, *args, **kwargs):
        super(StaticFileBaseExtractor, self).__init__(*args, **kwargs)

        if 'file_url' not in self.source_definition:
            raise ConfigurationError('Missing \'file_url\' definition')

        if not self.source_definition['file_url']:
            raise ConfigurationError('The \'file_url\' is empty')

        self.file_url = self.source_definition['file_url']

    def extract_items(self, static_content):
        """Parses the static content and extracts the items.

        This method must be implemented by the class that inherits the
        :py:class:`StaticFileBaseExtractor` and should return a generator
        that yields an item per iteration. Items should be formatted
        as tuples containing the following elements (in this order):

        - the content-type of the data retrieved from the source (e.g.
          ``application/json``)
        - the data in it's original format, as retrieved from the source
          (as a string)

        :param static_content: the retrieved static content containing
                               the items.
        :type static_content: str.
        """
        raise NotImplementedError

    def run(self):
        # Retrieve the static content from the source
        r = self.http_session.get(self.file_url)
        r.raise_for_status()

        static_content = r.content

        # Extract and yield the items
        for item in self.extract_items(static_content):
            yield item


class StaticXmlExtractor(StaticFileBaseExtractor):
    """Extract items from a single static XML file.

    The XPath expression used to extract items from the retrieved
    XML file should be specified in the definition of the source
    by populating the ``item_xpath`` attribute.
    """

    def __init__(self, *args, **kwargs):
        super(StaticXmlExtractor, self).__init__(*args, **kwargs)

        if 'item_xpath' not in self.source_definition:
            raise ConfigurationError('Missing \'item_xpath\' definition')

        if not self.source_definition['item_xpath']:
            raise ConfigurationError('The \'item_xpath\' is empty')

        self.item_xpath = self.source_definition['item_xpath']

    def extract_items(self, static_content):
        tree = etree.fromstring(static_content)

        for item in tree.xpath(self.item_xpath):
            yield 'application/xml', etree.tostring(item)
