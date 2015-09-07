import json
import os
from datetime import datetime

from lxml import etree

from ocd_backend.items.rce import RCEItem

from . import ItemTestCase


class RCEItemTestCase(ItemTestCase):
    def setUp(self):
        super(RCEItemTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        self.source_definition = {
            'id': 'rce',
            'extractor': (
                'ocd_backend.extractors.oai.OaiExtractor'),
            'transformer': 'ocd_backend.transformers.BaseTransformer',
            'item': (
                'ocd_backend.items.rce.RCEItem'),
            'loader': 'ocd_backend.loaders.ElasticsearchLoader',
            'oai_base_url': (
                'http://cultureelerfgoed.adlibsoft.com/oaiapi/oai.ashx'),
            'oai_metadata_prefix': 'oai_dc',
            'oai_set': 'fotos'}

        with open(os.path.abspath(os.path.join(
            self.PWD, '../test_dumps/rce_item.xml')
        ), 'r') as f:
            self.raw_item = f.read()
        self.item = etree.XML(self.raw_item)

        self.collection = u'Rijkscultureel Erfgoed Beeldbank'
        self.rights = u'http://creativecommons.org/licenses/by-sa/3.0/'
        self.original_object_id = u'collect:20000001'
        self.original_object_urls = {
            u'html': u'http://beeldbank.cultureelerfgoed.nl/20000001',
            u'xml': (
                u'http://cultureelerfgoed.adlibsoft.com/oaiapi/oai.ashx?verb='
                u'GetRecord&identifier=collect:20000001&metadataPrefix='
                u'oai_dc')}
        self.media_urls = [{
            'original_url': (
                u'http://images.memorix.nl/rce/thumb/800x800/'
                'd99c8594-4a8c-acf9-b498-6f3a0a4e5f4b.jpg'),
            'content_type': 'image/jpeg'
        }, {
            'original_url': (
                u'http://images.memorix.nl/rce/thumb/400x400/'
                'd99c8594-4a8c-acf9-b498-6f3a0a4e5f4b.jpg'),
            'content_type': 'image/jpeg'}]
        self.title = u'Exterieur, overzicht voorgevel pand Vrouwenverband'
        self.date_str = '1998-07'
        self.date = datetime.strptime(self.date_str, '%Y-%m')
        self.date_granularity = 6

    def _instantiate_item(self):
        """
        Instantiate the item from the raw and parsed item we have
        """
        return RCEItem(
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

    def test_title(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        self.assertEqual(data['title'], self.title)

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
