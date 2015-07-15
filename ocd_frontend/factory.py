import os

from flask import Flask
from celery import Celery

from ocd_frontend.helpers import register_blueprints
from ocd_frontend.es import ElasticsearchService


def create_app_factory(package_name, package_path, settings_override=None):
    """Returns a :class:`Flask` application instance configured with
    project-wide functionality.

    :param package_name: application package name.
    :param package_path: application package path.
    :param settings_override: a dictionary of settings to override.
    """
    app = Flask(package_name, instance_relative_config=True)

    app.config.from_object('ocd_frontend.settings')
    app.config.from_object(settings_override)

    app.es = ElasticsearchService(app.config['ELASTICSEARCH_HOST'],
                                  app.config['ELASTICSEARCH_PORT'])

    register_blueprints(app, package_name, package_path)

    return app


def create_celery_app(app=None):
    app = app or create_app_factory('ocd_frontend.rest.celery', os.path.dirname(__file__))
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
