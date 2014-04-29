from celery.contrib.methods import task
from elasticsearch import Elasticsearch

from ocd_backend.settings import (ELASTICSEARCH_HOST, ELASTICSEARCH_PORT,
                                  EXECUTE_ASYNC)
from ocd_backend.log import get_source_logger
from ocd_backend.settings import EXECUTE_ASYNC

log = get_source_logger('loader')

class BaseLoader(object):
    """The base class that other loaders should inhert."""

    def __init__(self, source_definition):
        self.source_definition = source_definition

    def load_item(self, item):
        raise NotImplemented


class ElasticsearchLoader(BaseLoader):
    def __init__(self, *args, **kwargs):
        super(ElasticsearchLoader, self).__init__(*args, **kwargs)

    @task(name='ocd_backend.loaders.BaseLoader.load_item', ignore_result=True)
    def load_item(self, item):
        es = Elasticsearch([{
            'host': ELASTICSEARCH_HOST,
            'port': ELASTICSEARCH_PORT
        }])

        log.info('Indexing documents...')
        es.index(index='ocd_combined_index', doc_type='item',
                 body=item['combined_index_doc'])
        es.index(index='ocd_%s' % self.source_definition['id'], doc_type='item',
                 body=item['index_doc'])
