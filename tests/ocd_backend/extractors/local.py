import os
from pprint import pprint

from ocd_backend.exceptions import ConfigurationError
from ocd_backend.extractors.local import (
    LocalPathBaseExtractor, LocalPathJSONExtractor
)

from . import ExtractorTestCase

class LocalPathBaseExtractorTestCase(ExtractorTestCase):
    def setUp(self):
        super(LocalPathBaseExtractorTestCase, self).setUp()
        self.source_definition["extractor"] = (
            "ocd_backend.extractors.local.LocalPathJSONExtractor")
        self.source_definition["path"] = os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '../test_dumps/marker_museum/'))
        self.source_definition["pattern"] = "*.jpg"
        self.source_definition["media_base_url"] = (
            "http://static.opencultuurdata.nl/marker_museum/")

        self.local_files = sorted([
            os.path.join(self.source_definition["path"], '10012.jpg'),
            os.path.join(self.source_definition["path"], '10012a.jpg')])

        self.extractor = LocalPathBaseExtractor(self.source_definition)

    def test_path_set(self):
        self.assertIn('path', self.source_definition)

    def test_no_path_set(self):
        source_def = self.source_definition
        source_def.pop('path')
        with self.assertRaises(ConfigurationError) as cm:
            LocalPathBaseExtractor(self.source_definition)

    def test_pattern_set(self):
        self.assertIn('pattern', self.source_definition)

    def test_no_pattern_set(self):
        source_def = self.source_definition
        source_def.pop('pattern')
        with self.assertRaises(ConfigurationError) as cm:
            LocalPathBaseExtractor(self.source_definition)

    def test_extract_item(self):
        with self.assertRaises(NotImplementedError) as nie:
            self.extractor.extract_item({})

    def test_list_files(self):
        files = sorted(self.extractor._list_files())
        self.assertEqual(self.extractor.path, self.source_definition["path"])
        self.assertEqual(files, self.local_files)

class LocalPathJSONExtractorTestCase(ExtractorTestCase):
    def setUp(self):
        super(LocalPathJSONExtractorTestCase, self).setUp()
        self.source_definition["extractor"] = (
            "ocd_backend.extractors.local.LocalPathJSONExtractor")
        self.source_definition["path"] = os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '../test_dumps/marker_museum/'))
        self.source_definition["pattern"] = "*.jpg"
        self.source_definition["media_base_url"] = (
            "http://static.opencultuurdata.nl/marker_museum/")

        self.local_files = sorted([
            os.path.join(self.source_definition["path"], '10012.jpg'),
            os.path.join(self.source_definition["path"], '10012a.jpg')])

        self.extractor = LocalPathJSONExtractor(self.source_definition)

    def test_extract_item(self):
        result = self.extractor.extract_item('x')
        self.assertEqual(result, ('application/json', '{"filename": "x"}',))
