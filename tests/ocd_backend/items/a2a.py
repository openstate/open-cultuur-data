from lxml import etree
import os

from ocd_backend.log import get_source_logger

from ocd_backend.items.openarchieven import OpenArchievenItem
from ocd_backend.items.ra_tilburg import RegionaalArchiefTilburgItem

from . import ItemTestCase

log = get_source_logger('loader')


class A2ATestCase(ItemTestCase):
    def setUp(self):
        super(A2ATestCase, self).setUp()
        self.PWD = os.path.dirname(__file__)

        self.source_definition = self._get_source_definition()
        self.raw_item = self._get_raw_item()
        self.item = self._get_item()
        self._set_default_values()

    def _set_default_values(self):
        raise NotImplementedError

    def _get_raw_item(self):
        raw_item = ''
        with open(
            os.path.abspath(
                os.path.join(
                    self.PWD,
                    '../test_dumps/%s_item.xml' % (self._get_source_id(),)
                )
            ), 'r'
        ) as f:
            raw_item = f.read()
        return raw_item

    def _get_item(self):
        raw_item = self._get_raw_item()
        return etree.XML(raw_item)

    def _get_source_id(self):
        raise NotImplementedError

    def _get_oai_base_url(self):
        raise NotImplementedError

    def _get_source_definition(self):
        return {
            'id': self._get_source_id(),
            'extractor': 'ocd_backend.extractors.oai.OaiExtractor',
            'transformer': 'ocd_backend.transformers.BaseTransformer',
            'item': 'ocd_backend.items.LocalDumpItem',
            'loader': 'ocd_backend.loaders.ElasticsearchLoader',
            'oai_base_url': self._get_oai_base_url(),
            'oai_metadata_prefix': "oai_a2a"
        }

    def _get_item_class(self):
        return NotImplementedError

    def _instantiate_item(self):
        item_class = self._get_item_class()
        return item_class(
            self.source_definition, 'application/xml', self.raw_item, self.item
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
        self.assertDictEqual(item.get_original_object_urls(),
                             self.original_object_urls)

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

    def test_combined_index_data_types(self):
        item = self._instantiate_item()
        data = item.get_combined_index_data()
        data['all_text'] = item.get_all_text()
        for field, field_type in item.combined_index_fields.iteritems():
            self.assertIn(field, data)
            if data[field] is not None:
                self.assertIsInstance(data[field], field_type)


class OpenArchievenTestCase(A2ATestCase):
    def _set_default_values(self):
        self.collection = u'Open Archieven'
        self.rights = u'Creative Commons Zero Public Domain'
        self.original_object_id = u'elo:000002e0-e965-e554-0ffd-fae16753075a'
        self.original_object_urls = {
            u'xml': (
                u'http://api.openarch.nl/oai-pmh/?verb=GetRecord&'
                u'metadataPrefix=oai_a2a&identifier='
                u'elo:000002e0-e965-e554-0ffd-fae16753075a'
            ),
            u'html': (
                u'http://www.openarch.nl/show.php?archive=elo'
                u'&identifier=000002e0-e965-e554-0ffd-fae16753075a'
            )
        }

    def _get_source_id(self):
        return 'openarchieven'

    def _get_oai_base_url(self):
        return 'http://api.openarch.nl/oai-pmh/'

    def _get_item_class(self):
        return OpenArchievenItem


class RegionaalArchiefTilburgTestCase(A2ATestCase):
    def _set_default_values(self):
        self.collection = u'Regionaal Archief Tilburg'
        self.rights = u'Creative Commons Zero Public Domain'
        self.original_object_id = u'000002dd-842d-fe78-0a08-8fb6209ae4f1'
        self.original_object_urls = {
            u'html': (
                u'http://www.regionaalarchieftilburg.nl/zoeken-in-databases/'
                u'genealogie/resultaten/weergave/akte/layout/default/id/'
                u'000002dd-842d-fe78-0a08-8fb6209ae4f1'
            ),
            u'xml': (
                u'http://api.memorix-maior.nl/collectiebeheer/a2a/key/'
                u'42de466c-8cb5-11e3-9b8b-00155d012a18/tenant/tlb'
                u'?verb=GetRecord&metadataPrefix=oai_a2a&identifier='
                u'000002dd-842d-fe78-0a08-8fb6209ae4f1'
            )
        }

    def _get_source_id(self):
        return 'ra_tilburg'

    def _get_oai_base_url(self):
        return (
            'http://api.memorix-maior.nl/collectiebeheer/a2a/key/'
            '42de466c-8cb5-11e3-9b8b-00155d012a18/tenant/tlb'
        )

    def _get_item_class(self):
        return RegionaalArchiefTilburgItem
