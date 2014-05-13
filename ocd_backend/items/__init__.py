from hashlib import sha1
from datetime import datetime
from collections import MutableMapping

from ocd_backend.exceptions import UnableToGenerateObjectId


class BaseItem(object):
    """Represents a single extracted and transformed item.

    :param source_definition: The configuration of a single source in
        the form of a dictionary (as defined in the settings).
    :type source_definition: dict
    :param data_content_type: The content-type of the data retrieved
        from the source (e.g. ``application/json``).
    :type data_content_type: str
    :param data: The data in it's original format, as retrieved
        from the source.
    :type data: unicode
    :param item: the deserialized item retrieved from the source.
    :param processing_started: The datetime we started processing this
        itme. If ``None``, the current datetime is used.
    :type processing_started: datetime or None
    """

    #: Allowed key-value pairs for the item's meta
    meta_fields = {
        'processing_started': datetime,
        'processing_finished': datetime,
        'source': unicode,
        'rights': unicode,
        'original_object_id': unicode,
        'original_object_urls': dict,
        'object_types': list
    }

    #: Allowed key-value pairs for the document inserted int he 'combined index'
    combined_index_fields = {
        'title': unicode,
        'description': unicode,
        'date': datetime,
        'date_granularity': int,
        'authors': list,
        'media_urls': list,
        'all_text': unicode
    }

    def __init__(self, source_definition, data_content_type, data, item,
                 processing_started=None):
        self.source_definition = source_definition
        self.data_content_type = data_content_type
        self.data = data
        self.original_item = item

        # On init, all data should be available to construct self.meta
        # and self.combined_item
        self._construct_object_meta(processing_started)
        self._construct_combined_index_data()

        self.index_data = self.get_index_data()

    def _construct_object_meta(self, processing_started=None):
        self.meta = StrictMappingDict(self.meta_fields)
        if not processing_started:
            self.meta['processing_started'] = datetime.now()

        self.meta['source'] = unicode(self.source_definition['id'])
        self.meta['rights'] = self.get_rights()
        self.meta['original_object_id'] = self.get_original_object_id()
        self.meta['original_object_urls'] = self.get_original_object_urls()
        self.meta['object_types'] = self.get_object_types()

    def _construct_combined_index_data(self):
        self.combined_index_data = StrictMappingDict(self.combined_index_fields)

        for field, value in self.get_combined_index_data().iteritems():
            if value:
                self.combined_index_data[field] = value

    def get_combined_index_doc(self):
        """Construct the document that should be inserted into the 'combined
        index'.

        :returns: a dict ready to be indexed.
        :rtype: dict
        """
        combined_item = {}

        combined_item['meta'] = dict(self.meta)
        combined_item.update(dict(self.combined_index_data))
        combined_item['all_text'] = self.get_all_text()

        return combined_item

    def get_index_doc(self):
        """Construct the document that should be inserted into the index
        belonging to the item's source.

        :returns: a dict ready for indexing.
        :rtype: dict
        """
        item =  {}

        item['meta'] = dict(self.meta)
        item['source_data'] = {
            'content_type': self.data_content_type,
            'data': self.data
        }
        item.update(dict(self.combined_index_data))
        item.update(self.index_data)

        return item

    def get_original_object_id(self):
        """Retrieves the ID used by the source for identify this item.

        This method should be implmented by the class that inherits from
        :class:`.BaseItem`.

        :rtype: unicode.
        """
        raise NotImplementedError

    def get_object_id(self):
        """Generates a new object ID which is used within OCD to identify
        the item.

        By default, we use a hash containing the id of the source, the
        original object id of the item (:meth:`~.get_original_object_id`)
        and the original urls (:meth:`~.get_original_object_urls`).

        :raises UnableToGenerateObjectId: when both the original object
            id and urls are missing.
        :rtype: str
        """
        try:
            object_id = self.get_original_object_id()
        except NotImplementedError:
            object_id = u''

        try:
            urls = self.get_original_object_urls()
        except NotImplementedError:
            urls = {}

        if not object_id and not urls:
            raise UnableToGenerateObjectId('Both original id and urls missing')

        hash_content = self.source_definition['id'] + object_id + ''.join(sorted(urls.values()))

        return sha1(hash_content).hexdigest()

    def get_original_object_urls(self):
        """Retrieves the item's original URLs at the source location.
        The keys of the returned dictionary should be named after the
        document format to which the value of the dictionary item, the
        URL, points (e.g. ``json``, ``html`` or ``csv``).

        This method should be implmented by the class that inherits from
        :class:`.BaseItem`.

        :rtype: dict.
        """
        raise NotImplementedError

    def get_rights(self):
        """Retrieves the rights of the item as defined by the source.
        With 'rights' we mean information about copyright, licenses,
        instructions for reuse, etcetera. "Creative Commons Zero" is an
        example of a possible value of rights.

        This method should be implmented by the class that inherits from
        :class:`.BaseItem`.

        :rtype: unicode.
        """
        raise NotImplementedError

    def get_object_types(self):
        """Retrieves a list containing the types of this item. Some
        examples of types are: "schilderij", "beeldhouwwerk", "film",
        etcetera.

        This method should be implmented by the class that inherits from
        :class:`.BaseItem`.

        :rtype: list.
        """
        raise NotImplementedError

    def get_combined_index_data(self):
        """Returns a dictionary containing the data that is suitable to
        be indexed in a combined/normalized repository, togehter with
        items from other collections. Only keys defined in
        :attr:`.combined_index_fields`
        are allowed.

        This method should be implmented by the class that inherits from
        :class:`.BaseItem`.

        :rtype: dict
        """
        raise NotImplementedError

    def get_index_data(self):
        raise NotImplementedError

    def get_all_text(self):
        """Retrieves all textual content of the item as a concatenated
        string. This text is used in the combined index to allow
        retrieving content that is not included in one of the
        :attr:`.combined_index_fields` fields.

        This method should be implmented by the class that inherits from
        :class:`.BaseItem`.

        :rtype: unicode.
        """
        raise NotImplementedError


class StrictMappingDict(MutableMapping):
    """A dictionary that can only contain a select number of predefined
    key-value pairs.

    When setting an item, the key is first checked against
    mapping. If the key is not in the mapping, a :exc:`KeyError` is
    raised. If the value is not of the datetype that is specified in the
    mapping, a :exc:`TypeError` is raised.

    :param mapping: the mapping of allowed keys and value datatypes.
    :type mapping: dict
    """

    def __init__(self, mapping):
        self.mapping = mapping

        self.store = {}

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        if key not in self.mapping:
            raise KeyError('According to the mapping, %s is not in allowed' % key)
        elif type(value) is not self.mapping[key]:
            raise TypeError('Value of %s must be %s, not %s'
                            % (key, self.mapping[key], type(value)))
        else:
            self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)
