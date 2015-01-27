import json
import os
from datetime import datetime

from lxml import etree

from ocd_backend.items.nabeeldbank import NationaalArchiefBeeldbankItem

from . import ItemTestCase


class NationaalArchiefBeeldbankItemTestCase(ItemTestCase):
    def setUp(self):
        super(NationaalArchiefBeeldbankItemTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        self.source_definition = {
            'id': 'nationaal_archief_beeldbank',
            'extractor': (
                'ocd_backend.extractors.opensearch.OpensearchExtractor'),
            'transformer': 'ocd_backend.transformers.BaseTransformer',
            'item': (
                'ocd_backend.items.nabeeldbank.NationaalArchiefBeeldbankItem'),
            'loader': 'ocd_backend.loaders.ElasticsearchLoader',
            'opensearch_url': (
                'http://www.gahetna.nl/beeldbank-api/opensearch/'),
            'opensearch_query': '"*:*"'
        }

        with open(os.path.abspath(os.path.join(
            self.PWD, '../test_dumps/nationaal_archief_beeldbank_item.xml')
        ), 'r') as f:
            self.raw_item = f.read()
        self.item = etree.XML(self.raw_item)

        self.collection = u'Beeldbank Nationaal Archief'
        self.rights = u'http://creativecommons.org/licenses/by-sa/3.0/deed.nl'
        self.original_object_id = u'ae98579a-d0b4-102d-bcf8-003048976d84'
        self.original_object_urls = {
            u'html': (
                u'http://hdl.handle.net/10648/'
                u'ae98579a-d0b4-102d-bcf8-003048976d84')}
        self.media_urls = [{
            'original_url': (
                'http://afbeeldingen.gahetna.nl/naa/thumb/800x600/'
                '8e6606c4-bad0-4009-b708-acdb4062ab39.jpg'),
            'content_type': 'image/jpeg',
            'width': 800,
            'height': 600}]
        self.date_str = '1932-11-30T00:00:00Z'
        self.date = datetime.strptime(self.date_str, '%Y-%m-%dT%H:%M:%SZ')
        self.date_granularity = 14

    def _instantiate_item(self):
        """
        Instantiate the item from the raw and parsed item we have
        """
        return NationaalArchiefBeeldbankItem(
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

    def test_correct_date(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        self.assertIn('date', data)
        self.assertEqual(data['date'], self.date)
        self.assertEqual(data['date_granularity'], self.date_granularity)

    def test_faulty_date(self):
        self.raw_item = self.raw_item.replace(
            '<dc:date>' + self.date_str + '</dc:date>',
            '<dc:date>0002-11-30T00:00:00Z</dc:date>')
        self.item = etree.XML(self.raw_item)
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        self.assertNotIn('date', data)
        self.assertEqual(data['date_granularity'], self.date_granularity)

    def test_combined_index_data_types(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        for field, field_type in item.combined_index_fields.iteritems():
            if data.get(field, None) is not None:
                self.assertIsInstance(data[field], field_type)
