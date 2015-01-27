import os.path

DEBUG = True

# Celery settings
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1'

# Elasticsearch
ELASTICSEARCH_HOST = '127.0.0.1'
ELASTICSEARCH_PORT = 9200

# The default number of hits to return for a search request via the REST API
DEFAULT_SEARCH_SIZE = 10

# The max. number of hits to return for a search request via the REST API
MAX_SEARCH_SIZE = 100

# The name of the index containing documents from all sources
COMBINED_INDEX = 'ocd_combined_index'

# The default prefix used for all ocd data
DEFAULT_INDEX_PREFIX = 'ocd'

# The fields which can be used for sorting results via the REST API
SORTABLE_FIELDS = (
    'meta.source_id', 'meta.processing_started', 'meta.processing_finished',
    'date', 'date_granularity', 'authors', '_score'
)

# Definition of the ES facets (and filters) that are accessible through
# the REST API
AVAILABLE_FACETS = {
    # 'retrieved_at': {
    #     'date_histogram': {
    #         'field': 'retrieved_at',
    #         'interval': 'month'
    #     }
    # },
    'rights': {
        'terms': {
            'field': 'meta.rights',
            'size': 10
        }
    },
    'source_id': {
        'terms': {
            'field': 'meta.source_id',
            'size': 10
        }
    },
    'collection': {
        'terms': {
            'field': 'meta.collection'
        }
    },
    'author': {
        'terms': {
            'field': 'authors.untouched',
            'size': 10
        }
    },
    'date': {
        'date_histogram': {
            'field': 'date',
            'interval': 'month'
        }
    },
    'date_granularity': {
        'terms': {
            'field': 'date_granularity',
            'size': 10
        }
    },
    'media_content_type': {
        'terms': {
            'field': 'media_urls.content_type',
            'size': 10
        }
    }
}

# The allowed date intervals for an ES data_histogram that can be
# requested via the REST API
ALLOWED_DATE_INTERVALS = ('day', 'week', 'month', 'quarter', 'year')

# Name of the Elasticsearch index used to store URL resolve documnts
RESOLVER_URL_INDEX = 'ocd_resolver'

# Determines if API usage events should be logged
USAGE_LOGGING_ENABLED = True
# Name of the Elasticsearch index used to store logged events
USAGE_LOGGING_INDEX = 'ocd_usage_logs'

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DUMPS_DIR = os.path.join(os.path.dirname(ROOT_PATH), 'dumps')
LOCAL_DUMPS_DIR = os.path.join(os.path.dirname(ROOT_PATH), 'local_dumps')

# URL where of the API instance that should be used for management commands
# Should include API version and a trailing slash.
# Can be overridden in the CLI when required, for instance when the user wants
# to download dumps from another API instance than the one hosted by OpenState
API_URL = 'http://api.opencultuurdata.nl/v0/'

# URL where collection dumps are hosted. This is used for generating full URLs
# to dumps in the /dumps endpoint
DUMP_URL = 'http://dumps.opencultuurdata.nl/'

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
try:
    from local_settings import *
except ImportError:
    pass
