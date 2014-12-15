import json
import random

from flask import url_for
from flask.ext.testing import TestCase

from ocd_frontend import rest, settings
from .mixins import FlaskTestCaseMixin


class FrontEndTestCase(FlaskTestCaseMixin, TestCase):

    def create_app(self):
        """
        Create instance of Flask application for testing.
        :return:
        """
        app = rest.create_app(settings_override={
            'TESTING': True
        })
        self.es_client = app.es.es

        return app

    def setUp(self):
        # Elasticsearch should be running for the tests
        self.assertTrue(self.es_client.ping(), msg='Elasticsearch cluster is not '
                                              'running')
        self.es_client.indices.create('ocd_testindex')
        # TODO: We should generate some test data for testing purposes

    def tearDown(self):
        self.es_client.indices.delete('ocd_testindex')

    def test_search(self):
        url = url_for('api.search')
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de'}))
        self.assert_ok_json(response)

    def test_missing_query(self):
        """'query' is a required search parameter"""
        url = url_for('api.search')
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'not-a-query': 'de'}))
        self.assert_bad_request_json(response)

    def test_sort_query(self):
        url = url_for('api.search')
        sort_field = random.choice(settings.SORTABLE_FIELDS)
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'sort': sort_field}))
        self.assert_ok_json(response)

    def test_sort_query_order(self):
        url = url_for('api.search')
        sort_field = random.choice(settings.SORTABLE_FIELDS)
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
        sort_field = random.choice(settings.SORTABLE_FIELDS)
        response = self.post(url, content_type='application/json',
                             data=json.dumps({'query': 'de',
                                              'order': 'upsidedown',
                                              'sort': sort_field}))
        self.assert_bad_request_json(response)
