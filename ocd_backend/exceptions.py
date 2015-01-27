class ConfigurationError(Exception):
    """Thrown when a setting in sources.json is missing or has
    an improper value."""


class NotFound(Exception):
    """Indicates that a requested item does not exist."""


class UnableToGenerateObjectId(Exception):
    """Indicates that the 'object_id' can't be generated."""


class NoDeserializerAvailable(Exception):
    """Thrown when there is no deserializer available for the
    content-type of an."""


class FieldNotAvailable(Exception):
    """Exception thrown when a field could not be found."""
    def __init__(self, field):
        self.field = field

    def __str__(self):
        return repr(self.field)
