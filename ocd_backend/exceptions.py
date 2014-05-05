class NotFound(Exception):
    """Indicates that a requested item does not exist."""


class UnableToGenerateObjectId(Exception):
    """Indicates that the 'object_id' can't be generated."""

class NoDeserializerAvailable(Exception):
    """Thrown when there is no deserializer avilable for the
    content-type of an."""
