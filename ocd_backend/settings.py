import os

CELERY_CONFIG = {
    'BROKER_URL': 'redis://127.0.0.1:6379/0',
    'CELERY_RESULT_BACKEND': 'redis://127.0.0.1:6379/0'
}

LOGGING = {
    'version': 1,
    'formatters': {
        'console': {
            'format': '[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
    },
    'loggers': {
        'ocd_backend': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}

ELASTICSEARCH_HOST = '127.0.0.1'
ELASTICSEARCH_PORT = 9200

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# The path of the JSON file containing the sources config
SOURCES_CONFIG_FILE = os.path.join(ROOT_PATH, 'sources.json')

# The name of the index containing documents from all sources
COMBINED_INDEX = 'ocd_combined_index'

# The default prefix used for all ocd data
DEFAULT_INDEX_PREFIX = 'ocd'

RESOLVER_BASE_URL = 'http://localhost:5000/v0/resolve'
RESOLVER_URL_INDEX = 'ocd_resolver'


# The User-Agent that is used when retrieving data from external sources
USER_AGENT = 'OpenCultuurData/0.1 (+http://www.opencultuurdata.nl/)'

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
try:
    from local_settings import *
except ImportError:
    pass
