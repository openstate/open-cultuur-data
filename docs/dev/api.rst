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

Loading items
-------------

.. autoclass:: ocd_backend.loaders.BaseLoader
   :members: run, load_item

.. autoclass:: ocd_backend.loaders.ElasticsearchLoader
