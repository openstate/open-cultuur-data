import os

from lxml import etree

from ocd_backend.items.museum_rotterdam import MuseumRotterdamItem

from . import ItemTestCase


class MuseumRotterdamItemTestCase(ItemTestCase):
    def setUp(self):
        super(MuseumRotterdamItemTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        self.source_definition = {
            'id': 'test_definition',
            'extractor': (
                'ocd_backend.extractors.staticfile.'
                'StaticXmlExtractor'
            ),
            'transformer': 'ocd_backend.transformers.BaseTransformer',
            'item': 'ocd_backend.items.museum_rotterdam.MuseumRotterdamItem',
            'loader': 'ocd_backend.loaders.ElasticsearchLoader',
            "file_url": (
                "http://static.opencultuurdata.nl/museum_rotterdam/"
                "MuseumRotterdamCollectie19082014.xml"),
            "item_xpath": "//cb3:record",
            "default_namespace": "cb3",
            "cb3_mapping": {
                "inventarisnummer": 1,
                "extensie": 5,
                "titel": 48,
                "objecttrefwoorden": 2,
                "materiaal": 14,
                "afmetingen": 15,
                "datering_beginjaar": 18,
                "datering_eindjaar": 19,
                "plaats_vervaardiging": 20,
                "technieken": 21,
                "vervaardiger": 22,
                "beschrijving": 3,
                "opschrift_merken": 17,
                "trefwoorden": 51,
                "associatie": 23,
                "herkomst": 40,
                "licentie": 85
            }
        }

        with open(os.path.abspath(os.path.join(
            self.PWD, '../test_dumps/museum_rotterdam_item.xml')), 'r'
        ) as f:
            self.raw_item = f.read()
        self.item = etree.XML(self.raw_item)

        self.collection = u'Museum Rotterdam'
        self.rights = u'https://creativecommons.org/publicdomain/mark/1.0/'
        self.original_object_id = u'4'
        self.original_object_urls = {
            u'html': u'http://museumrotterdam.nl/collectie/item/4'
        }
        self.media_urls = [{
            'original_url': (
                u'http://museumrotterdam.nl/cache/lowres/4_1_700_700.jpg'),
            'content_type': 'image/jpeg'}]

    def _instantiate_item(self):
        return MuseumRotterdamItem(
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
            item.get_original_object_id(), self.original_object_id)

    def test_get_original_object_urls(self):
        item = self._instantiate_item()
        self.assertDictEqual(
            item.get_original_object_urls(), self.original_object_urls)

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
