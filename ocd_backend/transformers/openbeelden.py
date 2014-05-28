from ocd_backend.transformers import BaseTransformer
from ocd_backend.utils.misc import parse_oai_response

class OpenbeeldenTransformer(BaseTransformer):
    def deserialize_item(self, raw_item_content_type, raw_item):
        return parse_oai_response(raw_item)
