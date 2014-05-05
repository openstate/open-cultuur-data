.. _datasets:

Datasets
========

Rijksmuseum
-----------

This dataset contains items from the collection of the `Rijksmuseum <https://www.rijksmuseum.nl/>`_. Content is harvested by using the publicly accessible `Rijksmuseum API <http://rijksmuseum.github.io/>`_. Only Dutch content is indexed.


Combined index
^^^^^^^^^^^^^^

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``title``                            |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``description``        | ``description``                      |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``date``               | ``dating.early`` or ``dating.year``  | ``dating.early`` is preferred, but if  |
|                        |                                      | not present ``dating.year`` is used.   |
|                        |                                      | The ``date_granularity`` indicates how |
|                        |                                      | precise the stored ``date`` is.        |
+------------------------+--------------------------------------+----------------------------------------+
| ``authors``            | ``principalMakers.name``             |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``webImage``                         | ``media_urls`` contains a array entry  |
|                        |                                      | width an object that contains details  |
|                        |                                      | from ``webImage`` (``url``, ``width``, | 
|                        |                                      | ``height`` and ``content_type``).      |
+------------------------+--------------------------------------+----------------------------------------+

Rijksmuseum index
^^^^^^^^^^^^^^^^^


Open Beelden
------------

This dataset contains audio, video and images from the `Open Beelden <http://www.openbeelden.nl/>`_. Content is harvested by using the `OAI-PMH feed <http://www.openbeelden.nl/api.nl>`_. The OCD implementation uses the 'oai_oi' (OAI Open Images) data format. Only Dutch content is indexed.


Combined index
^^^^^^^^^^^^^^

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``oi:title``                         |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``description``        | ``oi:abstract``                      |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``date``               | ``oi:date``                          | It is assumed that all year, moth and  |
|                        |                                      | day is known for all dates.            |
|                        |                                      | Therefor, ``date_granularity`` is      |
|                        |                                      | always 8 when a date is present.       |
+------------------------+--------------------------------------+----------------------------------------+
| ``authors``            | ``oi:attributionName``               |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``oi:medium`` and ``oi:extent``      | Each ``media_url`` entry contains an   |
|                        |                                      | object for each ``oi:medium`` node.    |
|                        |                                      | The value of ``oi:extent`` is stored   | 
|                        |                                      | under ``duration`` and represented as  |
|                        |                                      | seconds.                               |
+------------------------+--------------------------------------+----------------------------------------+


Open Beelden index
^^^^^^^^^^^^^^^^^^
