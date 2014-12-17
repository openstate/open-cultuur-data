import glob
import json
import os.path
import random

from flask import url_for, current_app
from flask.ext.testing import TestCase

from ocd_frontend import rest
from .mixins import FlaskTestCaseMixin


class FrontEndTestCase(FlaskTestCaseMixin, TestCase):

    def create_app(self):
        """
        Create instance of Flask application for testing.
        :return:
        """
        app = rest.create_app()
        app.config['TESTING'] = True
        app.config['COMBINED_INDEX'] = 'ocd_test_combined_index'
        app.config['RESOLVER_URL_INDEX'] = 'ocd_test_resolver'

        self.es_client = app.es.es
        self.PWD = os.path.dirname(__file__)

        return app

    def setUp(self):
        # Elasticsearch should be running for the tests
        self.assertTrue(self.es_client.ping(), msg='Elasticsearch cluster is not '
                                              'running')
        indices = ['ocd_test_combined_index'] #, 'ocd_testindex', 'ocd_test_resolver']
        self.add_indices(indices)

        doc_files = glob.glob(os.path.join(self.PWD, 'test_data/test_combined/*.json'))
        # Index some test data
        for f in doc_files:
            with open(f, 'rb') as doc_file:
                doc = json.load(doc_file)
                # Explicitly refresh index, as the upcoming count request can
                # be faster to execute than the refresh rate of the ES instance
                self.es_client.index(index='ocd_test_combined_index', body=doc,
                                     doc_type='item', refresh=True)

        # Check if every test document is actually indexed
        self.assertEqual(
            self.es_client.count(index='ocd_test_combined_index').get('count'),
            len(doc_files)
        )
        # TODO: We should have a better way of generating test data

    def add_indices(self, indices):
        """
        Add indices specified in ``self.indices``, and register cleanup method
        for each one.
        """
        for index in indices:
            if not self.es_client.indices.exists(index):
                self.es_client.indices.create(index)
                self.addCleanup(self.remove_index, index)

    def remove_index(self, index_name):
        self.es_client.indices.delete(index_name)

    def test_search(self):
        url = url_for('api.search')
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de'}))
        self.assert_ok_json(response)
        # import ipdb; ipdb.set_trace()

    def test_missing_query(self):
        """'query' is a required search parameter"""
        url = url_for('api.search')
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'not-a-query': 'de'}))
        self.assert_bad_request_json(response)

    def test_sort_query(self):
        url = url_for('api.search')
        sort_field = random.choice(current_app.config['SORTABLE_FIELDS'])
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'sort': sort_field}))
        self.assert_ok_json(response)

    def test_sort_query_order(self):
        url = url_for('api.search')
        sort_field = random.choice(current_app.config['SORTABLE_FIELDS'])
        sort_order = random.choice(['asc', 'desc'])
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de', 'order': sort_order,
                                              'sort': sort_field}))
        self.assert_ok_json(response)

    def test_sort_query_with_invalid_sort_field(self):
        url = url_for('api.search')
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'sort': 'not-a-sort-field'}))
        self.assert_bad_request_json(response)

    def test_sort_query_nonexisting_order(self):
        url = url_for('api.search')
        sort_field = random.choice(current_app.config['SORTABLE_FIELDS'])
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'order': 'upsidedown',
                                              'sort': sort_field}))
        self.assert_bad_request_json(response)

    def test_facets(self):
        url = url_for('api.search')

        available_facets = current_app.config['AVAILABLE_FACETS']
        facet_keys = random.sample(available_facets.keys(), 3)
        facets = {fk: available_facets[fk] for fk in facet_keys}

        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'facets': facets}))

        self.assert_ok_json(response)
        self.assertIn('facets', response.json)
        for fk in facet_keys:
            self.assertIn(fk, response.json.get('facets', {}))

    def test_not_available_facet(self):
        url = url_for('api.search')

        facets = {
            'rights-that-are-not-a-facet': {
                'terms': {
                    'field': 'meta.rights',
                    'size': 10
                }
            }
        }

        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'facets': facets}))
        self.assert_bad_request_json(response)

    def test_facet_size(self):
        url = url_for('api.search')

        facets = {
            'rights': {
                'terms': {
                    'field': 'meta.rights',
                    'size': 10
                }
            }
        }

        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'facets': facets}))
        self.assert_ok_json(response)

    def test_invalid_facet_size(self):
        url = url_for('api.search')

        facets = {
            'rights': {
                'terms': {
                    'field': 'meta.rights',
                    'size': 'abc'
                }
            }
        }

        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'facets': facets}))
        self.assert_bad_request_json(response)

    def test_datetime_facet(self):
        url = url_for('api.search')

        facets = {
            'date': {
                'date_histogram': {
                    'field': 'date',
                    'interval': 'month'
                }
            }
        }

        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'facets': facets}))
        self.assert_ok_json(response)

    def test_datetime_facet_interval_not_string(self):
        url = url_for('api.search')

        facets = {
            'date': {
                'date_histogram': {
                    'field': 'date',
                    'interval': 123
                }
            }
        }

        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'facets': facets}))
        self.assert_bad_request_json(response)

    def test_datetime_facet_interval_not_allowed(self):
        url = url_for('api.search')

        facets = {
            'date': {
                'date_histogram': {
                    'field': 'date',
                    'interval': 'millenium'
                }
            }
        }

        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'facets': facets}))
        self.assert_bad_request_json(response)

    def test_facet_should_be_dict(self):
        url = url_for('api.search')
        facets = ['some facet']
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'facets': facets}))
        self.assert_bad_request_json(response)

    def test_from(self):
        url = url_for('api.search')
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de', 'from': 10}))
        self.assert_ok_json(response)

    def test_invalid_value_from(self):
        url = url_for('api.search')
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de', 'from': 'abc'}))
        self.assert_bad_request_json(response)

    def test_negative_value_from(self):
        url = url_for('api.search')
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de', 'from': -1}))
        self.assert_bad_request_json(response)

    def test_size(self):
        url = url_for('api.search')
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de', 'size': 10}))
        self.assert_ok_json(response)

    def test_invalid_value_size(self):
        url = url_for('api.search')
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de', 'size': 'abc'}))
        self.assert_bad_request_json(response)

    def test_negative_value_size(self):
        url = url_for('api.search')
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de', 'size': -1}))
        self.assert_bad_request_json(response)
