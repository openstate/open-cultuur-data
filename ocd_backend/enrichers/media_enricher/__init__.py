import os
from tempfile import SpooledTemporaryFile

from requests import Session
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from ocd_backend.settings import TEMP_DIR_PATH, USER_AGENT
from ocd_backend.enrichers import BaseEnricher
from ocd_backend.exceptions import SkipEnrichment, UnsupportedContentType
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

    http_session = None

    def setup_http_session(self):
        if self.http_session:
            self.http_session.close()

        self.http_session = Session()
        self.http_session.headers['User-Agent'] = USER_AGENT

        http_retry = Retry(total=5, status_forcelist=[500, 503],
                           backoff_factor=.5)
        http_adapter = HTTPAdapter(max_retries=http_retry)
        self.http_session.mount('http://', http_adapter)

        http_retry = Retry(total=5, status_forcelist=[500, 503],
                           backoff_factor=.5)
        http_adapter = HTTPAdapter(max_retries=http_retry)
        self.http_session.mount('https://', http_adapter)

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

        http_resp = self.http_session.get(url, stream=True, timeout=(60, 120))
        http_resp.raise_for_status()

        if not os.path.exists(TEMP_DIR_PATH):
            log.debug('Creating temp directory %s' % TEMP_DIR_PATH)
            os.makedirs(TEMP_DIR_PATH)

        # Create a temporary file to store the media item, write the file
        # to disk if it is larger than 1 MB.
        media_file = SpooledTemporaryFile(max_size=1024*1024, prefix='ocd_m_',
                                          suffix='.tmp',
                                          dir=TEMP_DIR_PATH)

        for chunk in http_resp.iter_content(chunk_size=512*1024):
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

        self.setup_http_session()

        media_urls_enrichments = []
        for media_item in doc['media_urls']:
            media_item_enrichment = {}
            content_type, media_file = self.fetch_media(media_item['original_url'])

            for task in self.enricher_settings['tasks']:
                # Seek to the beginning of the file before starting a task
                media_file.seek(0)
                try:
                    self.available_tasks[task](media_item, content_type,
                                               media_file,
                                               media_item_enrichment,
                                               object_id, combined_index_doc,
                                               doc)
                except UnsupportedContentType:
                    log.debug('Skipping media enrichment task %s, '
                              'content-type %s (object_id: %s, url %s) is not '
                              'supported.' % (task, content_type, object_id,
                                              media_item['original_url']))
                    continue

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
