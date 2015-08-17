.. _dev_api:

Developer Interface
===================

.. module:: ocd_backend

Extracting items
----------------

.. autoclass:: ocd_backend.extractors.BaseExtractor
   :inherited-members:

.. autoclass:: ocd_backend.extractors.HttpRequestMixin
   :inherited-members:

.. autoclass:: ocd_backend.extractors.oai.OaiExtractor
   :members: oai_call, get_all_records

Transforming items
------------------

.. autoclass:: ocd_backend.transformers.BaseTransformer
   :members: run, transform_item

.. autoclass:: ocd_backend.items.BaseItem
   :members:
   :exclude-members: meta_fields, combined_index_fields

   .. autoattribute:: ocd_backend.items.BaseItem.meta_fields
      :annotation:

   .. autoattribute:: ocd_backend.items.BaseItem.combined_index_fields
      :annotation: 

.. autoclass:: ocd_backend.items.StrictMappingDict
   :members:

Enriching items
---------------

.. autoclass:: ocd_backend.enrichers.BaseEnricher
   :members: run, enrich_item

.. autoclass:: ocd_backend.enrichers.media_enricher.MediaEnricher
   :members: fetch_media, enrich_item

   .. autoattribute: ocd_backend.enrichers.media_enricher.MediaEnricher.available_tasks
      :annotation: 

Loading items
-------------

.. autoclass:: ocd_backend.loaders.BaseLoader
   :members: run, load_item

.. autoclass:: ocd_backend.loaders.ElasticsearchLoader

.. _dev_cli:

Command Line Interface
----------------------

The OpenCultuurData source code provides a Command Line Interface (CLI) for managing your instance. The CLI is largely self-documented (run ``./manage.py [<COMMAND>] --help`` for further assistance).

.. automodule:: manage


Dumps
+++++

.. autofunction:: create_dump

.. autofunction:: download_dumps

.. autofunction:: list_dumps

.. autofunction:: load_dump

Elasticsearch
+++++++++++++

.. autofunction:: es_put_template

.. autofunction:: es_put_mapping

.. autofunction:: create_indexes

.. autofunction:: delete_indexes

.. autofunction:: available_indices


Extract
+++++++

.. autofunction:: extract_list_sources

.. autofunction:: extract_start

Frontend
++++++++

.. autofunction:: frontend_runserver
