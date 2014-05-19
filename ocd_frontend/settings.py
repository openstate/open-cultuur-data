DEBUG = True
ELASTICSEARCH_HOST = '127.0.0.1'
ELASTICSEARCH_PORT = 9200

# The default number of hits to return for a search request via the REST API
DEFAULT_SEARCH_SIZE = 10

# The max. number of hits to return for a search request via the REST API
MAX_SEARCH_SIZE = 100

# The name of the index containing documents from all sources
COMBINED_INDEX = 'ocd_combined_index'

# The fields which can be used for sorting results via the REST API
SORTABLE_FIELDS = (
    'meta.source', 'meta.processing_started', 'meta.processing_finished',
    'date', 'date_granularity', 'authors', '_score'
)

# Defenition of the ES facets (and filters) that are accassible through
# the REST API
AVAILABLE_FACETS = {
    'retrieved_at': {
        'date_histogram': {
            'field': 'retrieved_at',
            'interval': 'month'
        }
    },
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
