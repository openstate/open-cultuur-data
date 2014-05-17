from celery import Celery

from ocd_backend.settings import CELERY_CONFIG

celery_app = Celery('ocd_backend', include=[
    'ocd_backend.extractors',
    'ocd_backend.transformers',
    'ocd_backend.loaders',
])

celery_app.conf.update(**CELERY_CONFIG)
