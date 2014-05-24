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

All API endpoints are designed according to the idea that there is an operation within a *context*: methods on the "root" context are executed across all datasets; :ref:`/search <rest_search>` executes a search across all collections, whereas :ref:`/openbeelden/search <rest_source_search>` executes a search on the OpenBeelden collection.

Arguments to an endpoint are placed behind the method definition, or supplied as JSON in a POST request. For instance, the :ref:`similar objects endpoint <rest_similar>` can be executed within the context of a collection, and needs an ``object_id`` to execute on.

.. Collection overview and statistics
.. ----------------------------------

.. .. http:get:: /collections

..    :statuscode 200: OK, no errors.

.. .. http:get:: /stats

..    :statuscode 200: OK, no errors.


.. _rest_search:

Searching within multiple collections
-------------------------------------

.. http:post:: /search

   Search for objects through all indexed datasets.

   **Example request**

   .. sourcecode:: http

      $ curl -i -XPOST 'http://<domain>/api/v0/search' -d '{
         "query": "journaal",
         "facets": {
            "collection": {},
            "date": {"interval": "day"}
         },
         "filters": {
            "media_content_type": {"terms": ["image/jpeg", "video/webm"]}
         },
         "size": 1
      }'

   **Example response**

    .. sourcecode:: http

       HTTP/1.0 200 OK
       Content-Type: application/json
       Content-Length: 1885
       Date: Mon, 19 May 2014 12:58:43 GMT

       {
         "facets": {
           "collection": {
             "_type": "terms",
             "missing": 0,
             "other": 0,
             "terms": [
               {
                 "count": 6,
                 "term": "Open Beelden"
               },
               {
                 "count": 2,
                 "term": "Rijksmuseum"
               }
             ],
             "total": 8
           },
           "date": {
             "_type": "date_histogram",
             "entries": [
               {
                 "count": 1,
                 "time": -652579200000
               },
               {
                 "count": 1,
                 "time": -573350400000
               },
               {
                 "count": 1,
                 "time": -552355200000
               },
               {
                 "count": 1,
                 "time": -541728000000
               },
               {
                 "count": 1,
                 "time": -259632000000
               },
               {
                 "count": 1,
                 "time": -239846400000
               },
               {
                 "count": 1,
                 "time": -239328000000
               },
               {
                 "count": 1,
                 "time": 1300233600000
               }
             ]
           }
         },
         "hits": {
           "hits": [
             {
               "_id": "4558763df1b233a57f0176839dc572e9e8726a02",
               "_score": 0.55381334,
               "_source": {
                 "meta": {
                   "collection": "Open Beelden",
                   "original_object_id": "oai:openimages.eu:654062",
                   "original_object_urls": {
                     "html": "http://openbeelden.nl/media/654062/",
                     "xml": "http://openbeelden.nl/feeds/oai/?verb=GetRecord&identifier=oai:openimages.eu:654062&metadataPrefix=oai_oi"
                   },
                   "processing_finished": "2014-05-19T13:18:04.770080",
                   "processing_started": "2014-05-19T13:18:04.761080",
                   "rights": "Creative Commons Attribution-ShareAlike",
                   "source_id": "openbeelden"
                 },
                 "title": "Postduivenvluchten in Nederland",
                 "authors": [
                   "Polygoon-Profilti (producent) / Nederlands Instituut voor Beeld en Geluid (beheerder)"
                 ],
                 "date": "1952-07-01T00:00:00",
                 "date_granularity": 8,
                 "description": "In dit journaal wordt verslag gedaan van de manier waarop een wedstrijdvlucht met postduiven wordt uitgevoerd...",
                 "media_urls": [
                   {
                     "content_type": "video/webm",
                     "url": "http://www.openbeelden.nl/files/06/54/654208.654061.WEEKNUMMER522-HRE0000D77F.webm"
                   },
                   {
                     "content_type": "video/ogg",
                     "url": "http://www.openbeelden.nl/files/06/54/654202.654061.WEEKNUMMER522-HRE0000D77F.ogv"
                   },
                   {
                     "content_type": "video/ogg",
                     "url": "http://www.openbeelden.nl/files/06/54/654200.654061.WEEKNUMMER522-HRE0000D77F.ogv"
                   },
                   {
                     "content_type": "video/mp4",
                     "url": "http://www.openbeelden.nl/files/06/54/654204.654061.WEEKNUMMER522-HRE0000D77F.mp4"
                   }
                 ]
               }
             }
           ],
           "max_score": 0.55381334,
           "total": 8
         },
         "took": 22
       }


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
         "media_content_type": {"count": 100},
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
   :jsonparameter filters: an object with field and values to filter on (optional).
   :jsonparameter facets: an object with fields for which to return facets (optional).
   :jsonparameter sort: the field the search results are sorted on. By default, results are sorted by relevancy to the query.
   :jsonparameter size: the maximum number of documents to return (optional, defaults to 10).
   :jsonparameter from: the offset from the first result (optional, defaults to 0).
   :statuscode 200: OK, no errors.
   :statuscode 400: Bad Request. An accompanying error message will explain why the request was invalid.

.. _rest_source_search:

Searching within a single collection
------------------------------------


.. http:post:: /(source_id)/search

   Search for objects within a specific dataset. The objects returned by this method will also include fields that are specific to the queried dataset, rather than only those fields that all indexed datasets have in common.

   See specifications of the :ref:`search method <rest_search>` for the request and response format.

   :jsonparameter query: on or more keywords.
   :jsonparameter filters: an object with field and values to filter on (optional).
   :jsonparameter facets: an object with fields for which to return facets (optional).
   :jsonparameter sort: the field the search results are sorted on. By default, results are sorted by relevancy to the query.
   :jsonparameter size: the maximum number of documents to return (optional, defaults to 10).
   :jsonparameter from: the offset from the first result (optional, defaults to 0).
   :statuscode 200: OK, no errors.
   :statuscode 400: Bad Request. An accompanying error message will explain why the request was invalid.
   :statuscode 404: The requested source does not exist.


Retrieving a single object
--------------------------

.. http:get:: /(source_id)/(object_id)

   Retrieve the contents of a single object.

   **Example request**

   .. sourcecode:: http

      $ curl -i 'http://<domain>/api/v0/openbeelden/4558763df1b233a57f0176839dc572e9e8726a02'

   **Example response**

   .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: application/json
      Content-Length: 2499
      Date: Mon, 19 May 2014 20:35:29 GMT

      {
        "meta": {
          "collection": "Open Beelden",
          "original_object_id": "oai:openimages.eu:654062",
          "original_object_urls": {
            "html": "http://openbeelden.nl/media/654062/",
            "xml": "http://openbeelden.nl/feeds/oai/?verb=GetRecord&identifier=oai:openimages.eu:654062&metadataPrefix=oai_oi"
          },
          "processing_finished": "2014-05-19T13:18:04.770080",
          "processing_started": "2014-05-19T13:18:04.761080",
          "rights": "Creative Commons Attribution-ShareAlike",
          "source_id": "openbeelden"
        },
        "title": "Postduivenvluchten in Nederland"
        "authors": [
          "Polygoon-Profilti (producent) / Nederlands Instituut voor Beeld en Geluid (beheerder)"
        ],
        "date": "1952-07-01T00:00:00",
        "date_granularity": 8,
        "description": "In dit journaal wordt verslag gedaan van de manier waarop een wedstrijdvlucht met postduiven wordt uitgevoerd...",
        "media_urls": [
          {
            "content_type": "video/webm",
            "url": "http://www.openbeelden.nl/files/06/54/654208.654061.WEEKNUMMER522-HRE0000D77F.webm"
          },
          {
            "content_type": "image/png",
            "url": "http://www.openbeelden.nl/images/654279/Postduivenvluchten_in_Nederland_%280_56%29.png"
          }
        ]
      }

   :statuscode 200: OK, no errors.
   :statuscode 404: The source and/or object does not exist.


.. http:get:: /(source_id)/(object_id)/source

   Retrieves the object's data in its original and unmodified form, as used as input for the Open Cultuur Data extractor(s). Being able to retrieve the object in it's original form can be useful for debugging purposes (i.e. when fields are missing or odd values are returned in the OCD representation of the object).

   The value of the ``Content-Type`` response header depends on the type of data that is returned by the data provider.

   **Example request**

   .. sourcecode:: http

      $ curl -i 'http://<domain>/api/v0/openbeelden/4558763df1b233a57f0176839dc572e9e8726a02/source'

   **Example response**

   .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: application/xml; charset=utf-8
      Content-Length: 3914
      Date: Mon, 19 May 2014 20:28:57 GMT

      <?xml version="1.0" encoding="UTF-8"?>
      <OAI-PMH xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.openarchives.org/OAI/2.0/" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
        ... snip ...
      </OAI-PMH>

   :statuscode 200: OK, no errors.
   :statuscode 404: The requested source and/or object does not exist.

.. _rest_similar:

Similar items
-------------

.. http:post:: /similar/(object_id)

  Retrieve objects similar to the object with id ``object_id`` across all indexed datasets (i.e. it could return similarly described paintings from different collection). From the contents of the object, the most descriptive terms ("descriptive" here means the terms with the highest tf-idf value in the document) are used to search across collections.

  As a search is executed, the response format is exactly the same as the response returned by the :ref:`search endpoint <rest_search>`. The request format is almost the same, with the exception that a query can't be specified (as the document with id ``object_id`` is considered the query). That means that faceting, filtering and sorting on the resulting set are fully supported.

  **Example request**

  .. sourcecode:: http

    $ curl -i -XPOST 'http://<domain>/api/v0/similar/<object_id>' -d '{
       "facets": {
          "collection": {},
          "date": {"interval": "day"}
       },
       "filters": {
          "media_content_type": {"terms": ["image/jpeg", "video/webm"]}
       },
       "size": 10,
       "from": 30,
       "sort": "date"
    }'

  :jsonparameter filters: an object with field and values to filter on (optional).
  :jsonparameter facets: an object with fields for which to return facets (optional).
  :jsonparameter sort: the field the search results are sorted on. By default, results are sorted by relevancy to the query.
  :jsonparameter size: the maximum number of documents to return (optional, defaults to 10).
  :jsonparameter from: the offset from the first result (optional, defaults to 0).
  :statuscode 200: OK, no errors.
  :statuscode 400: Bad Request. An accompanying error message will explain why the request was invalid.


.. http:post:: /(source_id)/similar/(object_id)

  Retrieve objects similar to the object with id ``object_id`` from the dataset specified by ``source_id``. You can find similar objects in the same collection, or objects in a different collection that are similar to the provided object.

  :jsonparameter filters: an object with field and values to filter on (optional).
  :jsonparameter facets: an object with fields for which to return facets (optional).
  :jsonparameter sort: the field the search results are sorted on. By default, results are sorted by relevancy to the query.
  :jsonparameter size: the maximum number of documents to return (optional, defaults to 10).
  :jsonparameter from: the offset from the first result (optional, defaults to 0).
  :statuscode 200: OK, no errors.
  :statuscode 400: Bad Request. An accompanying error message will explain why the request was invalid.
