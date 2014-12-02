from lxml import etree
import os
import datetime

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

    def test_get_event_type(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_event_type(), self.event_type
        )

    def test_get_event_place(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_event_place(), self.event_place
        )

    def test_get_institution_name(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_institution_name(), self.institution_name
        )

    def test_get_main_persons(self):
        item = self._instantiate_item()
        main_persons, all_persons = item._get_main_persons()
        self.assertEqual(
            main_persons, self.main_persons
        )

    def test_get_all_persons(self):
        item = self._instantiate_item()
        main_persons, all_persons = item._get_main_persons()
        self.assertEqual(
            all_persons, self.all_persons
        )

    def test_get_title(self):
        item = self._instantiate_item()
        main_persons, all_persons = item._get_main_persons()
        event_type = item._get_event_type()
        self.assertEqual(
            item._get_title(main_persons, event_type), self.title
        )

    def test_get_soure_type(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_source_type(), self.source_type
        )

    def test_get_soure_place(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_source_place(), self.source_place
        )

    def test_get_description(self):
        item = self._instantiate_item()
        main_persons, all_persons = item._get_main_persons()
        institution_name = item._get_institution_name()
        source_type = item._get_source_type()
        source_place = item._get_source_place()
        self.assertEqual(
            item._get_description(
                institution_name, source_type, source_place, all_persons
            ), self.description
        )

    def test_get_date_and_granularity(self):
        item = self._instantiate_item()
        date, granularity = item._get_date_and_granularity()
        self.assertEqual(
            date, self.date
        )
        self.assertEqual(
            granularity, self.date_granularity
        )

    def test_media_urls(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_media_urls(), self.media_urls
        )

    def test_document_number(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_document_number(), self.document_number
        )

    def test_book(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_book(), self.book
        )

    def test_source_collection(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_collection(), self.source_collection
        )

    def test_registry_number(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_registry_number(), self.registry_number
        )

    def test_archive_number(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_archive_number(), self.archive_number
        )

    def test_source_remark(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_source_remark(), self.source_remark
        )

    def test_authors(self):
        item = self._instantiate_item()
        self.assertEqual(
            item._get_authors(), self.authors
        )


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
        self.event_type = u'Registratie'
        self.event_place = None
        self.institution_name = u'Erfgoed Leiden en omstreken'
        self.main_persons = [u'Johanna Catharina Fakkel']
        self.all_persons = [u'Johanna Catharina Fakkel']
        self.title = u'Registratie, Johanna Catharina Fakkel'
        self.source_type = u'Bevolkingsregister'
        self.source_place = u'Leiden'
        self.description = (
            u'Erfgoed Leiden en omstreken, Bevolkingsregister, '
            u'Leiden, Johanna Catharina Fakkel'
        )
        self.date = datetime.datetime(1919, 2, 19)
        self.date_granularity = 8
        self.media_urls = []
        self.document_number = None
        self.book = u'01. A-Ba. (1 - 407)'
        self.source_collection = (
            u'Archiefnaam: Archief van het algemeen en dagelijks bestuur, '
            u'(1545) 1816-1929 (1963); Bevolkingsbo...'
        )
        self.registry_number = u'1305'
        self.archive_number = u'516'
        self.source_remark = None
        self.authors = []

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
        self.event_type = u'Registratie'
        self.event_place = None
        self.institution_name = u'Regionaal Archief Tilburg'
        self.main_persons = [u'Antonius Johannes Theodorus Luijten']
        self.all_persons = [u'Antonius Johannes Theodorus Luijten']
        self.title = u'Registratie, Antonius Johannes Theodorus Luijten'
        self.source_type = u'Bevolkingsregister'
        self.source_place = u'Goirle'
        self.description = (
            u'Regionaal Archief Tilburg, Bevolkingsregister, '
            u'Goirle, Antonius Johannes Theodorus Luijten'
        )
        self.date = None
        self.date_granularity = 0
        self.media_urls = [
            {
                'original_url': (
                    u'http://images.memorix.nl/tlb/thumb/140x140/'
                    u'4c70a2ff-1df9-56ce-85f3-74491f9d13ae.jpg'
                ),
                'content_type': 'image/jpeg'
            },
            {
                'original_url': (
                    u'http://images.memorix.nl/tlb/thumb/140x140/'
                    u'288f43a4-d5c4-54b5-30b3-b2e9910ad128.jpg'
                ),
                'content_type': 'image/jpeg'
            }
        ]
        self.document_number = None
        self.book = u'Inv. nr. 267 1910-1937 Gezinskaarten K-P'
        self.source_collection = (
            u'Archiefnaam: Bevolkingsregister Goirle, Bron: boek, Deel: 267, '
            u'Periode: 1910-1937'
        )
        self.registry_number = u'267'
        self.archive_number = u'0906'
        self.source_remark = None
        self.authors = []

    def _get_source_id(self):
        return 'ra_tilburg'

    def _get_oai_base_url(self):
        return (
            'http://api.memorix-maior.nl/collectiebeheer/a2a/key/'
            '42de466c-8cb5-11e3-9b8b-00155d012a18/tenant/tlb'
        )

    def _get_item_class(self):
        return RegionaalArchiefTilburgItem
