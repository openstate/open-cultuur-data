from unittest import TestCase

from ocd_frontend.rest.views import format_sources_results


class FormatSourcesResultsTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sources_results(self):
        input_data = {
            'aggregations': {
                'index': {
                    'buckets': [
                        {
                            'key': 'zoutkamp',
                            'collection': {
                                'buckets': [
                                    {
                                        'key': 'Zoutkamp',
                                        'doc_count': 204
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }

        result = format_sources_results(input_data)

        self.assertTrue(result.has_key('sources'))
        self.assertEqual(len(result['sources']), 1)
        self.assertEqual(result['sources'][0]['id'], 'zoutkamp')
        self.assertEqual(result['sources'][0]['name'], 'Zoutkamp')
        self.assertEqual(result['sources'][0]['count'], 204)
