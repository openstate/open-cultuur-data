from celery.contrib.methods import task

from ocd_backend.utils.misc import load_object

class BaseTransformer(object):
    def __init__(self, source_definition):
        self.source_definition = source_definition
        self.item_class = load_object(source_definition['item'])
        self.loader = load_object(source_definition['loader'])

    @task(name='ocd_backend.transformers.BaseTransformer.transform_item',
          ignore_result=True)
    def transform_item(self, raw_item_content_type, raw_item, item):
        self.raw_item_content_type = raw_item_content_type
        self.raw_item = raw_item
        self.item = item

        item = self.process_item()
        print '*' * 10
        print 'transform_item'
        loader = self.loader(self.source_definition)
        loader.load_item.delay({
          'combined_index_doc': item.get_combined_index_doc(),
          'index_doc': item.get_index_doc()
        })
        print '*' * 10


    def process_item(self):
        return self.item_class(self.source_definition,
                               self.raw_item_content_type,
                               self.raw_item,
                               self.item)
