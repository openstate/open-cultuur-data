from celery import Task
from elasticsearch import Elasticsearch

from ocd_backend.settings import ELASTICSEARCH_HOST, ELASTICSEARCH_PORT
from ocd_backend.log import get_source_logger

log = get_source_logger('loader')

class BaseLoader(Task):
    """The base class that other loaders should inhert."""

    def run(self, *args, **kwargs):
        """Start loading of a single item.

        This method is called by the transformer and expects args to
        contain the output of the transformer as a tuple.
        Kwargs should contain the ``source_definition`` dict.

        :param item:
        :param source_definition: The configuration of a single source in
            the form of a dictionary (as defined in the settings).
        :type source_definition: dict.
        :returns: the output of :py:meth:`~BaseTransformer.transform_item`
        """
        self.source_definition = kwargs['source_definition']

        return self.load_item(*args[0])

    def load_item(self, combined_index_doc, doc):
        raise NotImplemented


class ElasticsearchLoader(BaseLoader):
    """Indexes items into Elasticsearch.

    Each item is added to two indexes: a 'combined' index that contains
    items from different sources, and an index that only contains items
    of the same source as th item.
    """

    _es = None

    @property
    def es(self):
        """The Elasticsearch connection.

        :returns: instance of :class:`~elasticsearch.client.Elasticsearch`
        """
        if self._es is None:
            log.debug('Setting up Elasticsearch connection')
            self._es = Elasticsearch([{
                'host': ELASTICSEARCH_HOST,
                'port': ELASTICSEARCH_PORT
            }])

        return self._es

    def load_item(self, combined_index_doc, doc):
        log.info('Indexing documents...')
        self.es.index(index='ocd_combined_index', doc_type='item',
                      body=combined_index_doc)
        self.es.index(index='ocd_%s' % self.source_definition['id'], doc_type='item',
                      body=doc)
