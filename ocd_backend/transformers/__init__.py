from celery.contrib.methods import task

from ocd_backend.utils.misc import load_object

class BaseTransformer(object):
    def __init__(self, source_definition):
        self.source_definition = source_definition
        self.item_class = load_object(source_definition['item'])

    @task(name='ocd_backend.transformer.BaseTransformer.transform_item',
          ignore_result=True)
    def transform_item(self, raw_item_content_type, raw_item, item):
        print '*'*10
        print 'abc'
        item = self.item_class(self.source_definition, raw_item_content_type, raw_item, item)
        print item.get_combined_index_doc()
        print '*'*10
