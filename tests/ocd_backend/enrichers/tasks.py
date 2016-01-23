import os.path

from . import EnricherTestCase

from ocd_backend.enrichers.media_enricher import ImageMetadata

class EnricherTaskTestCase(EnricherTestCase):
    def setUp(self):
        self.smallImgsize = [800, 600]

    def test_get_size_indicator_correct(self):
        size_indicateor = ImageMetadata.get_size_indicator(self.smallImgsize)
        self.assertEqual(size_indicateor, 'small')

    def test_get_size_indicator_not_correct(self):
        size_indicateor = ImageMetadata.get_size_indicator(self.smallImgsize)
        self.assertNotEqual(size_indicateor, 'big')
