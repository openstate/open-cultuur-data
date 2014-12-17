import json
import os

from ocd_backend.items.gemeente_ede import GemeenteEdeItem

from . import ItemTestCase


class GemeenteEdeItemTestCase(ItemTestCase):
    def setUp(self):
        super(GemeenteEdeItemTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        self.source_definition = {
            'id': 'test_definition',
            'extractor': (
                'ocd_backend.extractors.staticfile.'
                'StaticJSONExtractor'
            ),
            'transformer': 'ocd_backend.transformers.BaseTransformer',
            'item': 'ocd_backend.items.gemeente_ede.GemeenteEdeItem',
            'loader': 'ocd_backend.loaders.ElasticsearchLoader',
            'file_url': ''
        }

        with open(
            os.path.abspath(
                os.path.join(self.PWD, '../test_dumps/gemeente_ede_item.json')
            ), 'r'
        ) as f:
            self.raw_item = f.read()
        with open(
            os.path.abspath(
                os.path.join(self.PWD, '../test_dumps/gemeente_ede_item.json')
            ), 'r'
        ) as f:
            self.item = json.load(f)

        self.collection = u'Gemeentearchief Ede'
        self.rights = u'http://creativecommons.org/licenses/by-sa/3.0/deed.nl'
        self.original_object_id = u'GA32573'
        self.original_object_urls = {
            u'html': u'https://commons.wikimedia.org/wiki/File:GA32573.jpg'
        }
        self.media_urls = [
            {
                'original_url': (
                    'https://upload.wikimedia.org/wikipedia/commons/b/b1/'
                    'Bijgebouw_van_jachthuis._-_A.B._Wigman_-_GA32573.jpg'
                ),
                'content_type': 'image/jpeg'
            }
        ]

    def test_item_collection(self):
        item = GemeenteEdeItem(
            self.source_definition, 'application/json',
            self.raw_item, self.item
        )
        self.assertEqual(item.get_collection(), self.collection)

    def test_get_rights(self):
        item = GemeenteEdeItem(
            self.source_definition, 'application/json',
            self.raw_item, self.item
        )
        self.assertEqual(item.get_rights(), self.rights)

    def test_get_original_object_id(self):
        item = GemeenteEdeItem(
            self.source_definition, 'application/json',
            self.raw_item, self.item
        )
        self.assertEqual(
            item.get_original_object_id(), self.original_object_id
        )

    def test_get_original_object_urls(self):
        item = GemeenteEdeItem(
            self.source_definition, 'application/json',
            self.raw_item, self.item
        )
        self.assertDictEqual(
            item.get_original_object_urls(), self.original_object_urls
        )

    def test_get_combined_index_data(self):
        item = GemeenteEdeItem(
            self.source_definition, 'application/json',
            self.raw_item, self.item
        )
        self.assertIsInstance(item.get_combined_index_data(), dict)

    def test_get_index_data(self):
        item = GemeenteEdeItem(
            self.source_definition, 'application/json',
            self.raw_item, self.item
        )
        self.assertIsInstance(item.get_index_data(), dict)

    def test_get_all_text(self):
        item = GemeenteEdeItem(
            self.source_definition, 'application/json',
            self.raw_item, self.item
        )
        self.assertEqual(type(item.get_all_text()), unicode)
        self.assertTrue(len(item.get_all_text()) > 0)

    def test_media_urls(self):
        item = GemeenteEdeItem(
            self.source_definition, 'application/json',
            self.raw_item, self.item
        )
        data = item.get_combined_index_data()
        self.assertEqual(data['media_urls'], self.media_urls)

    def test_combined_index_data_types(self):
        item = GemeenteEdeItem(
            self.source_definition, 'application/json',
            self.raw_item, self.item
        )
        data = item.get_combined_index_data()
        for field, field_type in item.combined_index_fields.iteritems():
            self.assertIn(field, data)
            self.assertIsInstance(data[field], field_type)
