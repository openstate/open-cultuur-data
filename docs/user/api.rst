.. _restapi:

RESTful API
===========

.. warning::

   This page currently shows a draft of the API specification. **The format of some of the request/response pairs is still subject to change!**

General notes
-------------

The API accepts requests with JSON content and returns JSON data in all of its responses (unless stated otherwise). Standard HTTP response codes are used to indicate errors. In case of an error, a more detailed description can be found in the JSON response body. UTF-8 character encoding is used in both requests and responses. 

All API URLs referenced in this documentation start with the following base part:

    :rest_api_v0:`None`

Collection overview and statistics
----------------------------------

.. http:get:: /collections

   :statuscode 200: OK, no errors.

.. http:get:: /stats

   :statuscode 200: OK, no errors.


Searching within multiple collections
-------------------------------------

.. http:post:: /search

   **Query**

   Besides standard keyword searches, a basic query syntax is supported. This syntax supports the following special characters:

   - ``+`` signifies an AND operation

   - ``|`` signifies an OR operation
   - ``-`` negates a single token
   - ``"`` wraps a number of tokens to signify a phrase for searching
   - ``*`` at the end of a term signifies a prefix query
   - ``(`` and ``)`` signify precedence

   The default strategy is to perform an AND query.

   **Facets**

   The ``facets`` object determines which facets should be returned. The keys of this object should contain the names of a the requested facets, the values should be objects. These objects are used to set per facet options. Facet defaults will be used when the options dictionary is empty.

   To specify the number of facet values that should be returned (for term based facets):

   .. sourcecode:: javascript

      {
         "media_type": {"count": 100},
         "author": {"count": 5}
      }

   For a date based facet the 'bucket size' of the histogram can be specified:

   .. sourcecode:: javascript

      {
         "date": {"interval": "year"}
      }

   Allowed sizes are ``year``, ``quarter``, ``month``, ``week`` and ``day`` (the default size is ``month``).

   **Filters**

   Results can be filtered on one ore more properties. Each key of the ``filters`` object represents a filter, the values should be objects. When filtering on multiple fields only documents that match all filters are included in the result set. The names of the filters match those of the facets.The names of the filters match those of the facets.

   For example, to retrieve documents that have media associated with them of the type ``image/jpeg`` **or** ``image/png`` **and** a  ``Rembrandt Harmensz. van Rijn`` as one of the authors:

   .. sourcecode:: javascript

      {
         "media_content_type": {
            "terms": ['image/jpeg', 'image/png']
         },
         "author": {
            "terms": ["Rembrandt Harmensz. van Rijn"]
         }
      }

   Use the following format to filter on a date range:

   .. sourcecode:: javascript

      {
         "date": {
            "from": "2011-12-24",
            "to": "2011-12-28"
         }
      }

   :jsonparameter query: on or more keywords.
   :jsonparameter filters: an array of filter objects (optional, defaults to ``null``).
   :jsonparameter enabled_facets: array containing the names of the facets that should be returned (optional, defaults to ``[]``).
   :jsonparameter facet_options: an object to specify options on a per facet basis (optional, defaults to ``null``)
   :jsonparameter size: the maximum number of documents to return (optional, defaults to 10).
   :jsonparameter from: the offset from the first result (optional, defaults to 0).
   :statuscode 200: OK, no errors.
   :statuscode 400: Bad Request. An accompanying error message will explain why the request was invalid.


Searching within a single collection
------------------------------------


Retrieving a single object
--------------------------

