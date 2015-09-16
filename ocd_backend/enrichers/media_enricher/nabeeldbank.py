from ocd_backend.enrichers.media_enricher import MediaEnricher


class NationaalArchiefEnricher(MediaEnricher):
    def enrich_item(self, enrichments, object_id, combined_index_doc, doc):
        # take only the first media item (or the first that is of a high resolution)
        # since enriching them all takes way too long
        media_item = doc['media_urls'][0]
        large_media_items = [m for m in doc['media_urls'] if u'/1280x' in m['original_url']]
        if len(large_media_urls) > 0:
            media_item = large_media_items[0]

        return super(NationaalArchiefEnricher, self).enrich_item(
            enrichments, object_id, combined_index_doc, {'media_urls': [media_item]})
