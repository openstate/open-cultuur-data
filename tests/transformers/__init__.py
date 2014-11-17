import json
import os.path
from unittest import TestCase


class TransformerTestCase(TestCase):

    def setUp(self):
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
            self.item = ('application/json', f.read())


from .base import BaseTransformerTestCase
