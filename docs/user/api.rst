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

