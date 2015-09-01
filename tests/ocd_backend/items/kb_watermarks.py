import json
import os

from lxml import etree

from ocd_backend.items.kb import WatermarksItem

from . import ItemTestCase


class WatermarksItemTestCase(ItemTestCase):
    def setUp(self):
        super(WatermarksItemTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        self.source_definition = {
            "id": "kb_watermarks",
            "extractor": "ocd_backend.extractors.oai.OaiExtractor",
            "transformer": "ocd_backend.transformers.BaseTransformer",
            "item": "ocd_backend.items.kb.WatermarksItem",
            "loader": "ocd_backend.loaders.ElasticsearchLoader",
            "oai_base_url": "http://services.kb.nl/mdo/oai",
            "oai_metadata_prefix": "dcx",
            "oai_set": "WILC"
        }

        with open(
            os.path.abspath(
                os.path.join(self.PWD, '../test_dumps/kb_watermarks_item.xml')
            ), 'r'
        ) as f:
            self.raw_item = f.read()
        self.item = etree.XML(self.raw_item)

        self.collection = u'Koninklijke Bibliotheek - Watermarks'
        self.rights = (
            u'http://creativecommons.org/publicdomain/zero/1.0/deed.nl'
        )
        self.original_object_id = u'WILC:WILC:57350'
        self.original_object_urls = {
            'xml': (
                'http://services.kb.nl/mdo/oai?verb=GetRecord&'
                'identifier=WILC:WILC:57350&metadataPrefix=dcx'
            ),
            'html': 'http://watermark.kb.nl/search/view/id/57350'
        }
        self.media_urls = [
            {
                'original_url': 'http://resolver.kb.nl/resolve?urn=WILC:57350',
                'content_type': 'image/jpeg'
            },
            {
                'original_url': (
                    'http://resolver.kb.nl/resolve?urn=WILC:57350'
                    '&role=thumbnail'
                ),
                'content_type': 'image/jpeg'
            }
        ]

    def _instantiate_item(self):
        return WatermarksItem(
            self.source_definition, 'application/xml',
            self.raw_item, self.item
        )

    def test_item_collection(self):
        item = self._instantiate_item()
        self.assertEqual(item.get_collection(), self.collection)

    def test_get_rights(self):
        item = self._instantiate_item()
        self.assertEqual(item.get_rights(), self.rights)

    def test_get_original_object_id(self):
        item = self._instantiate_item()
        self.assertEqual(
            item.get_original_object_id(), self.original_object_id
        )

    def test_get_original_object_urls(self):
        item = self._instantiate_item()
        self.assertDictEqual(
            item.get_original_object_urls(), self.original_object_urls
        )

    def test_get_combined_index_data(self):
        item = self._instantiate_item()
        self.assertIsInstance(item.get_combined_index_data(), dict)

    def test_get_index_data(self):
        item = self._instantiate_item()
        self.assertIsInstance(item.get_index_data(), dict)

    def test_get_all_text(self):
        item = self._instantiate_item()
        self.assertEqual(type(item.get_all_text()), unicode)
        self.assertTrue(len(item.get_all_text()) > 0)

    def test_media_urls(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        self.assertEqual(data['media_urls'], self.media_urls)

    def test_combined_index_data_types(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        for field, field_type in item.combined_index_fields.iteritems():
            self.assertIn(field, data)
            if data[field] is not None:
                self.assertIsInstance(data[field], field_type)
