import os
from tempfile import SpooledTemporaryFile

import requests

from ocd_backend import settings
from ocd_backend.enrichers import BaseEnricher
from ocd_backend.exceptions import SkipEnrichment
from ocd_backend.log import get_source_logger

from .tasks import ImageMetadata

log = get_source_logger('enricher')


class MediaEnricher(BaseEnricher):
    """An enricher that is responsible for enriching external media
    (images, audio, video, etc.) referenced in items (in the
    ``media_urls`` array).

    Media items are fetched from the source and then passed on to a
    set of registered tasks that are responsible for the analysis.
    """

    #: The registry of available sub-tasks that are responsible for the
    #: analysis of media items. Which tasks are executed depends on a
    #: combination of the configuration in ``sources.json`` and the
    #: returned ``content-type``.
    available_tasks = {
        'image_metdata': ImageMetadata
    }

    def fetch_media(self, url):
        """Retrieves a given media object from a remote (HTTP) location
        and returns the content-type and a file-like object containing
        the media content.

        The file-like object is a temporary file that - depending on the
        size - lives in memory or on disk. Once the file is closed, the
        contents are removed from storage.

        :param url: the URL of the media asset.
        :type url: str.
        :returns: a tuple with the ``content-type`` and a file-like object
            containing the media content.
        """

        http_resp = requests.get(url, stream=True)

        if not os.path.exists(settings.TEMP_DIR_PATH):
            log.debug('Creating temp directory %s' % settings.TEMP_DIR_PATH)
            os.makedirs(settings.TEMP_DIR_PATH)

        # Create a temporary file to store the media item, write the file
        # to disk if it is larger than 1 MB.
        media_file = SpooledTemporaryFile(max_size=1024*1024, prefix='ocd_m',
                                          suffix='tmp',
                                          dir=settings.TEMP_DIR_PATH)

        for chunk in http_resp.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive chunks
                media_file.write(chunk)

        media_file.flush()

        return http_resp.headers.get('content-type'), media_file

    def enrich_item(self, enrichments, object_id, combined_index_doc, doc):
        """Enriches the media objects referenced in a single item.

        First, a media item will be retrieved from the source, than the
        registered and configured tasks will run. In case fetching the
        item fails, enrichment of the media item will be skipped. In case
        a specific media enrichment task fails, only that task is
        skipped, which means that we move on to the next task.
        """

        if not doc.get('media_urls', []):
            raise SkipEnrichment('No "media_urls" in document.')

        media_urls_enrichments = []
        for media_item in doc['media_urls']:
            media_item_enrichment = {}
            content_type, media_file = self.fetch_media(media_item['original_url'])

            for task in self.enricher_settings['tasks']:
                # Seek to the beginning of the file before starting a task
                media_file.seek(0)
                self.available_tasks[task](media_item, content_type,
                                           media_file, media_item_enrichment,
                                           object_id, combined_index_doc, doc)

            media_item_enrichment['url'] = media_item['url']
            media_item_enrichment['original_url'] = media_item['original_url']
            media_item_enrichment['content_type'] = content_type

            # Move to the end of the file in order to determine it's
            # total size
            media_file.seek(0, 2)
            media_item_enrichment['size_in_bytes'] = media_file.tell()

            media_file.close()

            media_urls_enrichments.append(media_item_enrichment)

        enrichments['media_urls'] = media_urls_enrichments

        return enrichments
