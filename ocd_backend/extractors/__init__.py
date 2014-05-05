from ocd_backend.log import get_source_logger

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

    def run(self):
        """Starts the extraction process.

        This method must be implmented by the class that inherits the
        :py:class:`BaseExtractor` and should return a generator that
        yields one item per value. Items should be formatted as tuples
        containging the following elements (in this order):

        - the content-type of the data retrieved from the source (e.g.
          ``application/json``)
        - the data in it's original format, as retrieved from the source
          (as a string)
        - the deserialized item, as retrieved from the source
        """
        raise NotImplementedError
