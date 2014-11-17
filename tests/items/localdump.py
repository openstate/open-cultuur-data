import json
import os

from ocd_backend.items import LocalDumpItem

from . import ItemTestCase


class LocalDumpItemTestCase(ItemTestCase):
    def setUp(self):
        super(LocalDumpItemTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        dump_path = os.path.abspath(os.path.join(self.PWD, '../test_dumps/ocd_openbeelden_test.gz'))
        self.source_definition = {
            'id': 'test_definition',
            'extractor': 'ocd_backend.extractors.staticfile.StaticJSONDumpExtractor',
            'transformer': 'ocd_backend.transformers.BaseTransformer',
            'item': 'ocd_backend.items.LocalDumpItem',
            'loader': 'ocd_backend.loaders.ElasticsearchLoader',
            'dump_path': dump_path,
            'index_name': 'openbeelden'
        }
        with open(os.path.abspath(os.path.join(self.PWD, '../test_dumps/item.json')), 'r') as f:
            self.item = json.load(f)

    def test_something(self):
        print self.item
