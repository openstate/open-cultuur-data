from datetime import datetime
from ocd_backend.log import get_source_logger
from ocd_backend.items import BaseItem

from .a2a import A2AItem

log = get_source_logger('loader')


class RegionaalArchiefTilburgItem(A2AItem):
    def get_original_object_urls(self):
        identifier = self.get_original_object_id()
        return {
            'html': 'http://www.regionaalarchieftilburg.nl/zoeken-in-databases/genealogie/resultaten/weergave/akte/layout/default/id/%s' % (identifier),
            'xml': 'http://api.memorix-maior.nl/collectiebeheer/a2a/key/42de466c-8cb5-11e3-9b8b-00155d012a18/tenant/tlb?verb=GetRecord&metadataPrefix=oai_a2a&identifier=%s' % identifier
        }

    def get_rights(self):
        return u'Creative Commons Zero Public Domain'

    def get_collection(self):
        return u'Regionaal Archief Tilburg'
