import os
from datetime import datetime
import json

from lxml import etree

from ocd_backend.items.marker_museum import MarkerMuseumItem

from . import ItemTestCase


class MarkerMuseumItemTestCase(ItemTestCase):
    def setUp(self):
        super(MarkerMuseumItemTestCase, self).setUp()
        self.source_definition = {
            "id": "marker_museum",
            "extractor": "ocd_backend.extractors.local.LocalPathJSONExtractor",
            "transformer": "ocd_backend.transformers.BaseTransformer",
            "item":   "ocd_backend.items.marker_museum.MarkerMuseumItem",
            "enrichers": [
                [
                    "ocd_backend.enrichers.media_enricher.MediaEnricher",
                    {
                        "tasks": ["media_type", "image_metadata"]
                    }
                ]
            ],
            "loader": "ocd_backend.loaders.ElasticsearchLoader",
            "cleanup": "ocd_backend.tasks.CleanupElasticsearch",
            "index_name": "marker-museum",
            "path": os.path.abspath(os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                '../test_dumps/')),
            "pattern": "*.jpg",
            "media_base_url": "http://static.opencultuurdata.nl/marker_museum/"
        }


        self.raw_item = u'{"filename": "%s/marker_museum/10012.jpg"}' % (
            self.source_definition['path'],)
        self.item = json.loads(self.raw_item)

        self.collection = u'Marker Museum'
        self.rights = (
            u'http://creativecommons.org/publicdomain/zero/1.0/deed.nl')
        self.original_object_id = u'e20780c7887fc2bc8a47d8b1f8fbfbaf'
        self.title = u'marker museum'
        self.original_object_urls = {}
        self.media_urls = [{
            'original_url': (
                u'http://static.opencultuurdata.nl/marker_museum/'
                u'marker_museum/10012.jpg'
            ),
            'content_type': 'image/jpeg'
        }]
        self.date = None
        self.date_granularity = 0

    def _instantiate_item(self):
        """
        Instantiate the item from the raw and parsed item we have
        """
        return MarkerMuseumItem(
            self.source_definition, 'application/json',
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
            item.get_original_object_id(), self.original_object_id)

    def test_get_original_object_urls(self):
        item = self._instantiate_item()
        self.assertDictEqual(
            item.get_original_object_urls(), self.original_object_urls)

    def test_get_combined_index_data(self):
        item = self._instantiate_item()
        self.assertIsInstance(item.get_combined_index_data(), dict)

    def test_get_item_title(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        self.assertEqual(data['title'], self.title)

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
    #
    # def test_correct_date(self):
    #     item = self._instantiate_item()
    #     data = item.get_combined_index_data()
    #     self.assertIn('date', data)
    #     self.assertEqual(data['date'], self.date)
    #     self.assertEqual(data['date_granularity'], self.date_granularity)
    #
    def test_combined_index_data_types(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        for field, field_type in item.combined_index_fields.iteritems():
            if data.get(field, None) is not None:
                self.assertIsInstance(data[field], field_type)
