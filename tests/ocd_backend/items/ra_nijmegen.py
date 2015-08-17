import json
import os

from ocd_backend.items.ra_nijmegen import (
    NijmegenGrintenItem, NijmegenDoornroosjeItem, NijmegenVierdaagseItem)

from . import ItemTestCase


class NijmegenGrintenItemTestCase(ItemTestCase):
    def setUp(self):
        super(NijmegenGrintenItemTestCase, self).setUp()
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
            'file_url': ''
        }

        with open(os.path.abspath(os.path.join(
            self.PWD, (
                '../test_dumps/ra_nijmegen_grinten_item.json'))), 'r') as f:
            self.raw_item = f.read()
        with open(os.path.abspath(os.path.join(
            self.PWD, (
                '../test_dumps/ra_nijmegen_grinten_item.json'))), 'r') as f:
            self.item = json.load(f)

        self.collection = (
            u'Regionaal Archief Nijmegen - Fotocollectie Prof. dr. E.F. '
            u'van der Grinten')
        self.rights = u'https://creativecommons.org/licenses/by-sa/4.0/'
        self.original_object_id = u'F26235'
        self.original_object_urls = {
            u'html': (
                u'http://studiezaal.nijmegen.nl/ran/_detail.aspx?xmldescid='
                u'2113744396')}
        self.media_urls = [{
            'original_url': (
                u'http://www.nijmegen.nl/opendata/archief/vandergrinten/'
                u'F26235.jpg'),
            'content_type': 'image/jpeg'}]

    def _instantiate_item(self):
        return NijmegenGrintenItem(
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

    def test_combined_index_data_types(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        for field, field_type in item.combined_index_fields.iteritems():
            self.assertIn(field, data)
            if data[field] is not None:
                self.assertIsInstance(data[field], field_type)


class NijmegenDoornroosjeItemTestCase(ItemTestCase):
    def setUp(self):
        super(NijmegenDoornroosjeItemTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        self.source_definition = {
            'id': 'test_definition',
            'extractor': (
                'ocd_backend.extractors.staticfile.'
                'StaticJSONExtractor'
            ),
            'transformer': 'ocd_backend.transformers.BaseTransformer',
            'item': 'ocd_backend.items.gemeente_ede.NijmegenDoornroosjeItem',
            'loader': 'ocd_backend.loaders.ElasticsearchLoader',
            'file_url': ''
        }

        with open(os.path.abspath(os.path.join(
            self.PWD, (
                '../test_dumps/ra_nijmegen_doornroosje_item.json'))),
                'r') as f:
            self.raw_item = f.read()
        with open(os.path.abspath(os.path.join(
            self.PWD, (
                '../test_dumps/ra_nijmegen_doornroosje_item.json'))),
                'r') as f:
            self.item = json.load(f)

        self.collection = (
            u'Regionaal Archief Nijmegen - Affichecollectie Doornroosje')
        self.rights = u'https://creativecommons.org/licenses/by-sa/3.0/'
        self.original_object_id = u'AF1000.1000'
        self.original_object_urls = {
            u'html': (
                u'http://studiezaal.nijmegen.nl/ran/_detail.aspx?xmldescid='
                u'2010305578')}
        self.media_urls = [{
            'original_url': (
                u'http://www.nijmegen.nl/opendata/archief/AF1000.1000.JPG'),
            'content_type': 'image/jpeg'}]

    def _instantiate_item(self):
        return NijmegenDoornroosjeItem(
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

    def test_combined_index_data_types(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        for field, field_type in item.combined_index_fields.iteritems():
            self.assertIn(field, data)
            if data[field] is not None:
                self.assertIsInstance(data[field], field_type)


class NijmegenVierdaagseItemTestCase(ItemTestCase):
    def setUp(self):
        super(NijmegenVierdaagseItemTestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)
        self.source_definition = {
            'id': 'test_definition',
            'extractor': (
                'ocd_backend.extractors.staticfile.'
                'StaticJSONExtractor'
            ),
            'transformer': 'ocd_backend.transformers.BaseTransformer',
            'item': 'ocd_backend.items.gemeente_ede.NijmegenVierdaagseItem',
            'loader': 'ocd_backend.loaders.ElasticsearchLoader',
            'file_url': ''
        }

        with open(os.path.abspath(os.path.join(
            self.PWD, (
                '../test_dumps/ra_nijmegen_vierdaagse_item.json'))),
                'r') as f:
            self.raw_item = f.read()
        with open(os.path.abspath(os.path.join(
            self.PWD, (
                '../test_dumps/ra_nijmegen_vierdaagse_item.json'))),
                'r') as f:
            self.item = json.load(f)

        self.collection = (
            u'Fotocollectie Regionaal Archief Nijmegen - Vierdaagsefeesten'
            u' / Zomerfeesten')
        self.rights = u'https://creativecommons.org/licenses/by-sa/3.0/'
        self.original_object_id = u'F20706'
        self.original_object_urls = {
            u'html': (
                u'http://studiezaal.nijmegen.nl/ran/_detail.aspx?xmldescid='
                u'277219')}
        self.media_urls = [{
            'original_url': (
                u'http://www.nijmegen.nl/opendata/archief/F20706.jpg'),
            'content_type': 'image/jpeg'}]

    def _instantiate_item(self):
        return NijmegenVierdaagseItem(
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

    def test_combined_index_data_types(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        for field, field_type in item.combined_index_fields.iteritems():
            self.assertIn(field, data)
            if data[field] is not None:
                self.assertIsInstance(data[field], field_type)
