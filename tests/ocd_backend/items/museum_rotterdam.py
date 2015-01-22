import os

from lxml import etree

from ocd_backend.items.gemeente_ede import GemeenteEdeItem

from . import ItemTestCase


class MuseumRotterdamItemTestCase(ItemTestCase):
    def setUp(self):
        super(GemeenteEdeItemTestCase, self).setUp()
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
            'file_url': ''
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
            u'html': u'http://collectie.museumrotterdam.nl/objecten/4'
        }
        self.media_urls = [{
            'original_url': (
                'http://collectie.museumrotterdam.nl/beelden/4'),
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
