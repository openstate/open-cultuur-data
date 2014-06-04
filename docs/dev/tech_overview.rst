.. _dev_tech_overview:

Technical overview
==================

.. todo::

   Document the following:

   - ETL process
   - Used software

The OpenCultuurData (OCD) API consists of two main components; a frontend component consisting of a simple search interface and a RESTful API for accessing indexed collections, and a backend component which contains components to create configurable `ETL-pipelines <http://en.wikipedia.org/wiki/Extract,_transform,_load>`_ that can extract data from a collection, transform each item to an "OCD-compliant" format, and load those items in the OCD API.

RESTful api
-----------
The OCD API includes data from various collections, which each have very collection-specific metadata fields. An example would be clothes measurements for a fashion museum, or ``duration`` for a video collection. Therefore, items in the OCD API are stored in their own *collection*; metadata is stored on collection-level. Also, in order to facilitate search across collections, from the :ref:`common fields in the items <datasets_combinedindex>`, a general collection with **all** items is created as well.

The API exposes several functionalities on those collections, such as fulltext-search, a resolver for media-urls and a similar-to interface.

.. image:: /images/api-architecture.png

- :ref:`Full-text search <rest_search>`
- :ref:`GET individual items <rest_get>`
- :ref:`Resolve media urls <rest_resolver>`
- :ref:`Similar to <rest_similar>`
- ... (analysis, caching, ...)


Extract, Transform, Load, or ETL
--------------------------------
Loading data into the OCD API happens through ``pipelines``. A pipeline defines an extractor, a transformer and a loader. The task of an extractor is to queue individual items for the transformer. The transformer is tasked with extracting the fields relevant for both the combined index and the fields for the collection specific index. Also, this is where type casting, :ref:`determining the granularity of dates <date_granularity>` and additional analysis and enrichments take place.

.. image:: /images/etl.png

A pipeline can be defined in ``ocd_backend/sources.json``, by specifying a collection identifier, an extractor, transformer and a loader, as well as some pipeline specific environment variables (the Rijkmuseum pipeline requires an API key, for instance). Defining an extractor, transformer or loader are simply pointers to classes in ``ocd_backend/extractors``, ``ocd_backend/transformers`` and ``ocd_backend/loaders``, where a Python class lives that defines the behaviour required to perform extraction, transformation and loading.
