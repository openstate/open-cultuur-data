.. _dev_api:

Developer Interface
===================

.. module:: ocd_backend

Extracting items
----------------

.. autoclass:: ocd_backend.extractors.BaseExtractor
   :inherited-members:


Transforming items
------------------

.. autoclass:: ocd_backend.transformers.BaseTransformer
   :inherited-members:

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
