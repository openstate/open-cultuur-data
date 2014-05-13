from datetime import datetime

from celery import Task

from ocd_backend.es import elasticsearch
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

        object_id, combined_index_doc, doc = args[0]

        # Add the 'processing.finished' datetime to the documents
        finished = datetime.now()
        combined_index_doc['meta']['processing_finished'] = finished
        doc['meta']['processing_finished'] = finished

        return self.load_item(object_id, combined_index_doc, doc)

    def load_item(self, combined_index_doc, doc):
        raise NotImplemented


class ElasticsearchLoader(BaseLoader):
    """Indexes items into Elasticsearch.

    Each item is added to two indexes: a 'combined' index that contains
    items from different sources, and an index that only contains items
    of the same source as the item.
    """

    def load_item(self, object_id, combined_index_doc, doc):
        log.info('Indexing documents...')
        elasticsearch.index(index='ocd_combined_index', doc_type='item',
                            id=object_id, body=combined_index_doc)
        elasticsearch.index(index='ocd_%s' % self.source_definition['id'],
                            doc_type='item', id=object_id, body=doc)
