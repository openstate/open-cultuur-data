import os
import fnmatch
import json

from ocd_backend.extractors import BaseExtractor
from ocd_backend.exceptions import ConfigurationError


class LocalPathBaseExtractor(BaseExtractor):
    """ A class for implementing extractors that retrieve items
    by listing files in a local path."""

    def __init__(self, *args, **kwargs):
        super(LocalPathBaseExtractor, self).__init__(*args, **kwargs)

        if 'path' not in self.source_definition:
            raise ConfigurationError('Missing \'path\' definition')

        if not self.source_definition['path']:
            raise ConfigurationError('The \'path\' is empty')

        if 'pattern' not in self.source_definition:
            raise ConfigurationError('Missing \'pattern\' definition')

        if not self.source_definition['pattern']:
            raise ConfigurationError('The \'pattern\' is empty')

        self.path = self.source_definition['path']
        self.pattern = self.source_definition['pattern']

    def extract_item(self, filename):
        """Traverses the local directory and extracts the files as items.

        This method must be implemented by the class that inherits the
        :py:class:`StaticFileBaseExtractor` and should return a generator
        that yields an item per iteration. Items should be formatted
        as tuples containing the following elements (in this order):

        - the content-type of the data retrieved from the source (e.g.
          ``application/json``)
        - the data in it's original format, as retrieved from the source
          (as a string)

        :param filename: the local filename containing the item
        :type filename: str.
        """
        raise NotImplementedError

    def _list_files(self):
        """Traverses the path specified in the sourc definition and returns
        a list of local files.
        """

        files = []
        for dp, dn, fs in os.walk(self.path):
            files = files + [
                os.path.join(dp, f) for f in fnmatch.filter(fs, self.pattern)]
        return files

    def run(self):
        files = self._list_files()

        # Extract and yield the items
        for filename in files:
            item = self.extract_item(filename)
            yield item


class LocalPathJSONExtractor(LocalPathBaseExtractor):
    """Extracts local files as leightweight JSON objects, containing only the
    file name."""

    def extract_item(self, filename):
        return 'application/json', json.dumps({'filename': filename})
