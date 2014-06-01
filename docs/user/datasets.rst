.. _datasets:

Datasets
========

Fotobank Nationaal Archief
--------------------------

This dataset contains historical photographs from the `National Archive <http://www.gahetna.nl/collectie/afbeeldingen/fotocollectie>`_. The `archive's OpenSearch API <http://www.gahetna.nl/over-ons/aa-data>`_ is used to harvest the content that the National Archive has made available under an open license.


Combined index
^^^^^^^^^^^^^^

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``title``                            |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``description``        | ``description``                      | Only included if it differs from the   |
|                        |                                      | title.                                 |
+------------------------+--------------------------------------+----------------------------------------+
| ``date``               | ``dc:date``                          | It is assumed that the full date-time  |
|                        |                                      | is known for all items. The            |
|                        |                                      | ``date_granularity`` is therefor       |
|                        |                                      | always 14.                             |
+------------------------+--------------------------------------+----------------------------------------+
| ``authors``            | ``dc:creator``                       | Author is not included if '[onbekend]'.|
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``ese:isShownBy``                    | Each ``media_url`` entry contains an   |
|                        |                                      | object for each ``ese:isShownBy`` node.|
|                        |                                      | The resolution of the images is        |
|                        |                                      | from the image URL.                    |
+------------------------+--------------------------------------+----------------------------------------+


Fotobank Nationaal Archief index
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



Open Beelden
------------

This dataset contains audio, video and images from `Open Beelden <http://www.openbeelden.nl/>`_. Content is harvested by using the `OAI-PMH feed <http://www.openbeelden.nl/api.nl>`_. The OCD implementation uses the 'oai_oi' (OAI Open Images) data format. Only Dutch content is indexed.


Combined index
^^^^^^^^^^^^^^

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``oi:title``                         |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``description``        | ``oi:abstract``                      |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``date``               | ``oi:date``                          | It is assumed that the year, month and |
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


Centraal Museum Utrecht
-----------

This dataset contains items from the collection of the `Centraal Museum Utrecht <https://www.centraalmuseum.nl/>`_.
Content is harvested from a static copy of an xml file downloaded from the linked file `here <http://www.opencultuurdata.nl/wiki/centraal-museum/>`_.


Combined index
^^^^^^^^^^^^^^

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``title``                            |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``description``        | ``label.text``                       | normally missing                       |
+------------------------+--------------------------------------+----------------------------------------+
| ``date``               | reconstructed from                   | ``production.date.start`` is taken     |
|                        | ``production.date.start`` and        | with a granularity reconstructed from  |
|                        | ``production.date.end``              | the string, and compared to            |
|                        |                                      | ``production.date.end`` with its       |
|                        |                                      | granularity to possibly decrease the   |
|                        |                                      | final ``date_granularity``             |
+------------------------+--------------------------------------+----------------------------------------+
| ``authors``            | ``creator``                          |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``reproduction.identifier_URL``      | relative url added to absolute         |
|                        |                                      | template                               |
+------------------------+--------------------------------------+----------------------------------------+

Centraal Museum Utrecht index
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


+------------------------+--------------------------------------+----------------------------------------+
| Index field            | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``measurements``       |  ``dimension.type``,                 | the order in the xml document          |
|                        |  ``dimension.value``,                | determines grouping, because we        |
|                        |  ``dimension.unit``                  | 'transpose the matrix'                 |
+------------------------+--------------------------------------+----------------------------------------+
| ``acquisition``        |  ``acquisition.date``                | ``date_granularity`` is reconstructed  |
|                        |  ``acquisition.method``              |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``creator_roles``      |  ``creator``, ``creator.role``       | also 'transposed'                      |
+------------------------+--------------------------------------+----------------------------------------+
| ``collections``        |  ``collections``                     |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``materials``          |  ``material``                        |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``tags``               |  ``object_name``                     |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``technique``          |  ``techniek.vrije.tekst``            |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``notes``              |  ``notes``                           |                                        |
+------------------------+--------------------------------------+----------------------------------------+
