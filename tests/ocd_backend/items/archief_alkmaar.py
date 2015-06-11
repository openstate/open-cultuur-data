import json
import os
from datetime import datetime

from lxml import etree

from ocd_backend.items.archiefalkmaar_bonda import ArchiefAlkmaarBondaItem

from . import ItemTestCase


class ArchiefAlkmaarItemTestCase(ItemTestCase):
    def setUp(self):
        super(ArchiefAlkmaarItemTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        self.source_definition = {
            'id': 'archief_alkmaar_bonda',
            'extractor': (
                'ocd_backend.extractors.opensearch.OpensearchExtractor'),
            'transformer': 'ocd_backend.transformers.BaseTransformer',
            'item': (
                'ocd_backend.items.archiefalkmaar_bonda.ArchiefAlkmaarBondaItem'),
            'loader': 'ocd_backend.loaders.ElasticsearchLoader'
        }

        with open(os.path.abspath(os.path.join(
            self.PWD, '../test_dumps/archief_alkmaar_item.xml')
        ), 'r') as f:
            self.raw_item = f.read()
        self.item = etree.XML(self.raw_item)

        self.collection = u'Reg Archief Alkmaar Bonda'
        self.rights = u'http://en.wikipedia.org/wiki/Public_domain'
        self.original_object_id = u'oai:d5dd999d-d98a-4ecc-a38f-04927a3fbe34:963f7248-a263-11e0-bf4a-bde4fca6c222'
        self.title = u'Elzenlaan 2-4. Gezicht op \'\'Huis Russenduin\'\''
        self.original_object_urls = {
            u'html': (
                u'http://www.regionaalarchiefalkmaar.nl/beeldbank/'
                u'd5dd999d-d98a-4ecc-a38f-04927a3fbe34/'),
            u'xml': (
                u'https://maior.memorix.nl/api/oai/raa/key/Bonda/?verb=GetRecord'
                u'&identifier=oai:d5dd999d-d98a-4ecc-a38f-04927a3fbe34:963f7248-a263-11e0-bf4a-bde4fca6c222'
                u'&metadataPrefix=ese'
                )}
        self.media_urls = [{
            'original_url': (
                u'https://images.memorix.nl/raa/thumb/2000x2000/'
                u'4d80982f-9720-4c6c-abb9-da0424141575.jpg'),
            'content_type': 'image/jpg'
        }]
        self.date_str = '1920-00-00'
        self.year = '1920'
        self.date = datetime.strptime(self.year, '%Y')
        self.date_granularity = 4

    def _instantiate_item(self):
        """
        Instantiate the item from the raw and parsed item we have
        """
        return ArchiefAlkmaarBondaItem(
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

    def test_correct_date(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        self.assertIn('date', data)
        self.assertEqual(data['date'], self.date)
        self.assertEqual(data['date_granularity'], self.date_granularity)

    def test_combined_index_data_types(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        for field, field_type in item.combined_index_fields.iteritems():
            if data.get(field, None) is not None:
                self.assertIsInstance(data[field], field_type)
