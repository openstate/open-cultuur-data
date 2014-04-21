from celery.contrib.methods import task

from ocd_backend.log import get_source_logger
from ocd_backend.utils.misc import load_object
from ocd_backend.settings import EXECUTE_ASYNC

log = get_source_logger('extractor')

class BaseExtractor(object):
    """The base class that other extractors should inhert."""

    def __init__(self, source_definition):
        """
        :param source_definition: The configuration of a single source in
            the form of a dictionary (as defined in the settings).
        :type source_definition: dict.
        """
        self.source_definition = source_definition
        self.transformer = load_object(source_definition['transformer'])

    def transform_item(self, retrieved_data_content_type, retrieved_data, item,
                       async=EXECUTE_ASYNC):
        """Sends a single item to the transformer defined in the
        :py:attr:`source_definition`. This method should be called
        directly after extracting an item.

        :param retrieved_data_content_type: The content-type of the data retrieved
            from the source (e.g. ``application/json``).
        :type retrieved_data_content_type: str
        :param retrieved_data: The data in it's original format, as retrieved
            from the source.
        :type retrieved_data: unicode
        :param item: the deserialized item retrieved from the source.
        :param item: the extracted item.
        :param async: determines if the item should be proccessed
            asynchronously (with Celery) or sequential (without Celery).
        :type async: bool.
        """
        t = self.transformer(self.source_definition)

        if async:
            t.transform_item.s(retrieved_data_content_type, retrieved_data, item).delay()
        else:
            t.transform_item(retrieved_data_content_type, retrieved_data, item)

    def start(self):
        """Starts the extraction process.

        This method should be implmented by the class that inherits
        the :py:class:`BaseExtractor`.
        """
        raise NotImplementedError

    @task(name='ocd_backend.extractor.BaseExtractor.run_extractor',
          ignore_result=True)
    def run_extractor(self):
        self.start()
