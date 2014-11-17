import json
import os.path

from . import LoaderTestCase
from ocd_backend.loaders import ElasticsearchLoader


class ESLoaderTestCase(LoaderTestCase):
    def setUp(self):
        super(ESLoaderTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        self.object_id = u'52c54e5be11b218b1a6df731634fda9fb2188d57'

        with open(os.path.join(self.PWD, '../test_dumps/combined_index_doc.json'), 'r') as f:
            self.combined_index_doc = json.load(f)

        with open(os.path.join(self.PWD, '../test_dumps/index_doc.json'), 'r') as f:
            self.index_doc = json.load(f)
