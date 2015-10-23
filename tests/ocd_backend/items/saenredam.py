import json
import os
from datetime import datetime

from ocd_backend.items.saenredam import SaenredamItem

from . import ItemTestCase


class SaenredamItemTestCase(ItemTestCase):
    def setUp(self):
        super(SaenredamItemTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        self.source_definition = {
            'id': 'test_definition',
            'extractor': (
                'ocd_backend.extractors.staticfile.'
                'StaticJSONExtractor'
            ),
            'transformer': 'ocd_backend.transformers.BaseTransformer',
            'item': 'ocd_backend.items.gemeente_ede.NijmegenGrintenItem',
            'loader': 'ocd_backend.loaders.ElasticsearchLoader',
            'file_url': '',
            'media_base_url': 'http://static.opencultuurdata.nl/utrechts_archief/saenredam/'
        }

        with open(os.path.abspath(os.path.join(
            self.PWD, (
                '../test_dumps/saenredam_item.json'))), 'r') as f:
            self.raw_item = f.read()
        with open(os.path.abspath(os.path.join(
            self.PWD, (
                '../test_dumps/saenredam_item.json'))), 'r') as f:
            self.item = json.load(f)

        self.collection = u'Het Utrechts Archief - Saenredam Collectie'
        self.rights = u'https://creativecommons.org/publicdomain/zero/1.0/deed.nl'
        self.original_object_id = u'28593'
        self.original_object_urls = {
            u'html': (
                u'http://www.hetutrechtsarchief.nl/collectie/beeldmateriaal/'
                u'tekeningen_en_prenten/1400-1410/28593')}
        self.media_urls = [{
            'original_url': (
                u'http://static.opencultuurdata.nl/utrechts_archief/saenredam/X34-28593.jpg'),
            'content_type': 'image/jpeg'}]
        self.item_date = datetime(1636, 10, 15)
        self.item_gran = 8
        self.title = u'Oudegracht bij de Stadhuisbrug'
        self.description = u'Gezicht op de Stadhuisbrug te Utrecht met links het huis Keyserrijk,'
        self.authors = [u'Saenredam, P.']

    def _instantiate_item(self):
        return SaenredamItem(
            self.source_definition, 'application/json',
            self.raw_item, self.item)

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

    def test_date_and_granularity(self):
        item = self._instantiate_item()
        item_gran, item_date = item._get_date_and_granularity()
        self.assertEqual(item_date, self.item_date)
        self.assertEqual(item_gran, self.item_gran)

    def test_title(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        self.assertEqual(data['title'], self.title)

    def test_description(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        self.assertTrue(data['description'].startswith(self.description))

    def test_authors(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        self.assertEqual(data['authors'], self.authors)

    def test_combined_index_data_types(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        for field, field_type in item.combined_index_fields.iteritems():
            self.assertIn(field, data)
            if data[field] is not None:
                self.assertIsInstance(data[field], field_type)
