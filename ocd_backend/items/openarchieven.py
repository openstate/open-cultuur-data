from datetime import datetime
from ocd_backend.log import get_source_logger
from ocd_backend.items import BaseItem

from .a2a import A2AItem

log = get_source_logger('loader')


class OpenArchievenItem(A2AItem):
    def get_original_object_urls(self):
        original_id = self.get_original_object_id()
        archive, identifier = original_id.split(":")
        return {
            'html': 'http://www.openarch.nl/show.php?archive=%s&identifier=%s' % (archive,identifier),
            'xml': 'http://api.openarch.nl/oai-pmh/?verb=GetRecord&metadataPrefix=oai_a2a&identifier=%s' % original_id
        }

    def get_rights(self):
        return u'Creative Commons Zero Public Domain'

    def get_collection(self):
        return u'Open Archieven'
