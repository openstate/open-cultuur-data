from flask.ext.testing import TestCase

from ocd_frontend import rest
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
        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass
