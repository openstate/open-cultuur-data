import json
import os
from datetime import datetime

from lxml import etree

from ocd_backend.items.elobeeldbank import ErfgoedLeidenBeeldbankItem

from . import ItemTestCase


class ErfgoedLeidenBeeldbankItemTestCase(ItemTestCase):
    def setUp(self):
        super(ErfgoedLeidenBeeldbankItemTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        self.source_definition = {
            'id': 'erfgoed_leiden_beeldbank',
            'extractor': (
                'ocd_backend.extractors.opensearch.OpensearchExtractor'),
            'transformer': 'ocd_backend.transformers.BaseTransformer',
            'item': (
                'ocd_backend.items.nabeeldbank.ErfgoedLeidenBeeldbankItem'),
            'loader': 'ocd_backend.loaders.ElasticsearchLoader',
            'opensearch_url': (
                'http://www.gahetna.nl/beeldbank-api/opensearch/'),
            'opensearch_query': '"*:*"'
        }

        with open(os.path.abspath(os.path.join(
            self.PWD, '../test_dumps/erfgoed_leiden.xml')
        ), 'r') as f:
            self.raw_item = f.read()
        self.item = etree.XML(self.raw_item)

        self.collection = u'Beeldbank Erfgoed Leiden en omstreken'
        self.rights = u'http://creativecommons.org/licenses/by-sa/3.0/deed.nl'
        self.original_object_id = u'lei:col1:dat12064:id127'
        self.original_object_urls = {
            u'html': (
                u'http://www.archiefleiden.nl/lei:col1:dat12064:id127')}
        self.media_urls = [{
            'original_url': (
                u'http://neon.pictura-hosting.nl/lei/lei_mrx_bld/thumbs/1200x1200/lei/00/LEI_DB_010/LEI_DAT_4453_10/LEI001006912.jpg'),
            'content_type': u'image/jpeg',
            'width': 1200,
            'height': 1200}]
        self.date_str = u'Circa 1948'
        self.date = None
        # self.date = datetime.strptime(u'1948-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
        self.date_granularity = 0

    def _instantiate_item(self):
        """
        Instantiate the item from the raw and parsed item we have
        """
        return ErfgoedLeidenBeeldbankItem(
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
        self.assertEqual(data['date_granularity'], self.date_granularity)
        self.assertEqual(data['date'], self.date)

    # def test_faulty_date(self):
    #     self.raw_item = self.raw_item.replace(
    #         '<dc:date>' + self.date_str + '</dc:date>',
    #         '<dc:date>0002-11-30T00:00:00Z</dc:date>')
    #     self.item = etree.XML(self.raw_item)
    #     item = self._instantiate_item()
    #     data = item.get_combined_index_data()
    #     self.assertNotIn('date', data)
    #     self.assertEqual(data['date_granularity'], self.date_granularity)

    def test_combined_index_data_types(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        for field, field_type in item.combined_index_fields.iteritems():
            if data.get(field, None) is not None:
                self.assertIsInstance(data[field], field_type)

    def test_faulty_link(self):
        with open(os.path.abspath(os.path.join(
            self.PWD,
            '../test_dumps/erfgoed_leiden_noimg.xml')
        ), 'r') as f:
            self.raw_item = f.read()
        self.item = etree.XML(self.raw_item)
        self.original_object_urls = {
            'html': (
                u'http://www.archiefleiden.nl/lei:col1:dat82017:id127')}

        item = self._instantiate_item()
        self.assertDictEqual(
            item.get_original_object_urls(), self.original_object_urls)
