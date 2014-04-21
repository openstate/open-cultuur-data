.. _restapi:

RESTful API
===========

.. warning::

   This page currently shows a draft of the API specification. **The format of some of the request/response pairs is still subject to change!**

General notes
-------------

The API accepts requests with JSON content and returns JSON data in all of its responses (unless stated otherwise). Standard HTTP response codes are used to indicate errors. In case of an error, a more detailed description can be found in the JSON response body. UTF-8 character encoding is used in both requests and responses. 

All API URLs referenced in this documentation start with the following base part::

    http://api.opencultuurdata.nl/v1

Collection overview and statistics
----------------------------------

.. http:get:: /collections

   :statuscode 200: OK, no errors.

.. http:get:: /stats

   :statuscode 200: OK, no errors.


Searching within multiple collections
-------------------------------------


Searching within a single collection
------------------------------------


Retrieving a single object
--------------------------

