from celery import Celery

celery_app = Celery('ocd_backend', broker='redis://127.0.0.1:6379/0',
                    backend='redis://127.0.0.1:6379/0',
                    include=[
                        'ocd_backend.extractors',
                        'ocd_backend.transformers',
                        'ocd_backend.loaders'
                    ])
