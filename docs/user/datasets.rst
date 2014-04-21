.. _datasets:

Datasets
========

Rijksmuseum
-----------

This datasets contains items from the collection of the `Rijksmuseum <https://www.rijksmuseum.nl/>`_. Content is harvested by using the publicly accessible `Rijksmuseum API <http://rijksmuseum.github.io/>`_.

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``title``                            |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``description``        | ``description``                      |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``date``               | ``dating.early`` or ``dating.year``  | ``dating.early`` is preferred, but if  |
|                        |                                      | not present ``dating.year`` is used.   |
|                        |                                      | The ``granularity`` indicates how      |
|                        |                                      | precise the stored ``date`` is.        |
+------------------------+--------------------------------------+----------------------------------------+
| ``authors``            | ``principalMakers.name``             |                                        |
+------------------------+--------------------------------------+----------------------------------------+

