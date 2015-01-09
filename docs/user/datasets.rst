.. _datasets:

Datasets
========

Beeldbank Erfgoed Leiden
------------------------

This dataset contains historical images from the `Erfgoed Leiden en omstreken <http://www.archiefleiden.nl/home/collecties/beeldmateriaal/zoeken-in-beeldmateriaal>`_. The `archive's OpenSearch API <http://www.opencultuurdata.nl/wiki/regionaal-archief-leiden-beeldbank/>`_ is used to harvest content
that the archive has made available under an open license.


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
| ``date``               | ``Datum_afbeelding`` or              |                                        |
|                        | ``dcterms:created`` or ``dc:date``   |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``authors``            | ``dc:creator``                       | Author is not included if '[onbekend]'.|
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``ese:isShownBy``                    | Each ``media_url`` entry contains an   |
|                        |                                      | object for each ``ese:isShownBy`` node.|
|                        |                                      | The resolution of the images is        |
|                        |                                      | from the image URL.                    |
+------------------------+--------------------------------------+----------------------------------------+

Beeldbank Erfgoed Leiden index
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Centraal Museum Utrecht
-----------------------

This dataset contains items from the collection of the `Centraal Museum Utrecht <https://www.centraalmuseum.nl/>`_. Currently, the data that is made available by the Centraal Museum Utrecht only covers their fashion collection.

Content is harvested from a static XML file that was made available to Open Cultuur Data. More information about the dataset and a link to the actual XML file can be found on `this wiki page <http://www.opencultuurdata.nl/wiki/centraal-museum/>`_.

Combined index
^^^^^^^^^^^^^^

+----------------------+---------------------------------+---------------------------------------+
| Combined index field |         Source field(s)         |                Comment                |
+======================+=================================+=======================================+
| ``title``            | ``title``                       |                                       |
+----------------------+---------------------------------+---------------------------------------+
| ``description``      | ``label.text``                  | normally missing                      |
+----------------------+---------------------------------+---------------------------------------+
| ``date``             | reconstructed from              | ``production.date.start`` is taken    |
|                      | ``production.date.start``       | with a granularity reconstructed from |
|                      |                                 | the string                            |
|                      |                                 | ``production.date.end`` is ignored.   |
+----------------------+---------------------------------+---------------------------------------+
| ``authors``          | ``creator``                     |                                       |
+----------------------+---------------------------------+---------------------------------------+
| ``media_urls``       | ``reproduction.identifier_URL`` | relative url added to absolute        |
|                      |                                 | template                              |
+----------------------+---------------------------------+---------------------------------------+

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


Fotobank Nationaal Archief
--------------------------

This dataset contains historical photographs from the `National Archive <http://www.gahetna.nl/collectie/afbeeldingen/fotocollectie>`_. The `archive's OpenSearch API <http://www.gahetna.nl/over-ons/aa-data>`_ is used to harvest the content that the National Archive has made available under an open license.

.. _datasets_combinedindex:

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

Fries Museum
-----------------------

This dataset contains items from the collection of the `Fries Museum <https://www.friesmuseum.nl/>`_. Currently, the data that is made available by the Fries Museum only covers their fashion collection.

Content is harvested from a static XML file and image files that were made available to Open Cultuur Data. More information about the dataset and a link to the actual files can be found on `this wiki page <http://www.opencultuurdata.nl/wiki/fries-museum/>`_.


Combined index
^^^^^^^^^^^^^^

+----------------------+-----------------------------+---------------------------------------+
| Combined index field |       Source field(s)       |                Comment                |
+======================+=============================+=======================================+
| ``title``            | ``title``                   |                                       |
+----------------------+-----------------------------+---------------------------------------+
| ``description``      | ``label.text``              | often missing                         |
+----------------------+-----------------------------+---------------------------------------+
| ``date``             | reconstructed from          | ``production.date.start`` is taken    |
|                      | ``production.date.start``   | with a granularity reconstructed from |
|                      |                             | the string                            |
|                      |                             | ``production.date.end`` is ignored.   |
+----------------------+-----------------------------+---------------------------------------+
| ``authors``          | ``creator``                 |                                       |
+----------------------+-----------------------------+---------------------------------------+
| ``media_urls``       | ``reproduction.identifier`` | identifier used for static image set  |
+----------------------+-----------------------------+---------------------------------------+

Fries Museum index
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+----------------------+--------------------------------------+----------------------------------------+
|     Index field      |           Source field(s)            |                Comment                 |
+======================+======================================+========================================+
| ``measurements``     | ``dimension.type``,                  | the order in the xml document          |
|                      | ``dimension.value``,                 | determines grouping, because we        |
|                      | ``dimension.unit``                   | 'transpose the matrix'                 |
+----------------------+--------------------------------------+----------------------------------------+
| ``acquisition``      | ``acquisition.date``                 | ``date_granularity`` is reconstructed  |
|                      | ``acquisition.method``               |                                        |
+----------------------+--------------------------------------+----------------------------------------+
| ``production_place`` | ``production.place``                 |                                        |
+----------------------+--------------------------------------+----------------------------------------+
| ``collections``      | ``collection``                       |                                        |
+----------------------+--------------------------------------+----------------------------------------+
| ``materials``        | ``material``                         |                                        |
+----------------------+--------------------------------------+----------------------------------------+
| ``tags``             | ``object_name``                      |                                        |
+----------------------+--------------------------------------+----------------------------------------+
| ``technique``        | ``technique``                        |                                        |
+----------------------+--------------------------------------+----------------------------------------+



Open Archieven
--------------

This dataset contains genealogical data from open archives, as aggregated by `Open Archives <http://www.openarch.nl/>`_. The index contains records from independent researchers as well as archives, like `Erfgoed Leiden en omstreken <http://www.opencultuurdata.nl/wiki/regionaal-archief-leiden-genealogische-data/>`_, `Gemeente Ede <http://www.opencultuurdata.nl/wiki/gemeente-ede-bevolking-gemeente-ede-1647-1913/>`_, `Gemeentearchief Tholen <http://www.opencultuurdata.nl/wiki/gemeente-tholen-genealogische-data-bevolkingsregisters-1803-1940-metadata-en-scans/>`_. Content is harvested by using the `OAI-PMH feed <http://www.openarch.nl/api/docs/oai-pmh/>`_. The OCD implementation uses the 'oai_a2a' (Archive 2 All) data format.

Combined index
^^^^^^^^^^^^^^

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``EventType`` and ``PersonName``     | Only names of 'main' persons in event  |
+------------------------+--------------------------------------+----------------------------------------+
| ``description``        | ``InstitutionName``, ``SourceType``, | Names of all related persons           |
|                        | ``SourcePlace`` and ``PersonName``   |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``date``               | ``EventDate``                        | ``date_granularity`` varies between 8  |
|                        |                                      | and 10                                 |
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``SourceAvailableScans``             | Thumbnails of records are (in general) |
|                        |                                      | hosted by the original archive         |
+------------------------+--------------------------------------+----------------------------------------+

Open Archieven index
^^^^^^^^^^^^^^^^^^^^

.. _data_openbeelden:

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

Amsterdam Museum
----------------

This dataset contains audio, video and images from `Amsterdam Museum <http://www.amsterdammuseum.nl/>`_. Content is harvested by using the `OAI-PMH feed <http://ahm.adlibsoft.com/oaix/oai.ashx>`_. The OCD implementation uses the 'oai_dc' (OAI Dublic Core) data format.

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``dc:title``                         |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``description``        | ``dc:abstract``                      |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``date``               | ``dc:date``                          | It is assumed that the year, month and |
|                        |                                      | day is known for all dates.            |
|                        |                                      | Therefor, ``date_granularity`` is      |
|                        |                                      | always 8 when a date is present.       |
+------------------------+--------------------------------------+----------------------------------------+
| ``authors``            | ``dc:creator``                       |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``oi:medium`` and ``oi:extent``      | Each ``media_url`` entry contains an   |
|                        |                                      | object for each ``oi:medium`` node.    |
|                        |                                      | The value of ``oi:extent`` is stored   |
|                        |                                      | under ``duration`` and represented as  |
|                        |                                      | seconds.                               |
+------------------------+--------------------------------------+----------------------------------------+

Universiteitsbibliotheek Utrecht – Maps
---------------------------------------

This dataset contains images of historical maps of the provinces Holland and Utrecht from the `Universiteitsbibliotheek Utrecht <http://bc.library.uu.nl/nl/node/206/>`_. Content is harvested by using the `OAI-PMH feed <http://www.openbeelden.nl/api.nl>`_. The OCD implementation uses the 'oai_dc' (OAI Dublin Core) data format.


Combined index
^^^^^^^^^^^^^^

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``dc:title``                         |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``description``        | ``dc:description``                   |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``date``               | ``dc:date``                          | All maps only have information on the  |
|                        |                                      | year of publication.                   |
|                        |                                      | The ``date_granularity`` is always 4.  |
+------------------------+--------------------------------------+----------------------------------------+
| ``authors``            | ``dc:creator``                       |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``dc:format`` and ``imgLocation``    | Each image has to be individually      |
|                        |                                      | retrieved through a separate request   |
|                        |                                      | to get the imgLocation. As also        |
|                        |                                      | discussed in the wiki. ``dc:format``   |
|                        |                                      | gived the mime-type of the image.      |
+------------------------+--------------------------------------+----------------------------------------+


Universiteitsbibliotheek Utrecht Maps index
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Visserijmuseum Zoutkamp
-----------------------

This dataset contains images  from the `Visserijmuseum Zoutkamp
<http://www.visserijmuseum.com/>`_.
Content is harvested by using the `Adlib API <http://api.adlibsoft.com/site/>`_.


Combined index
^^^^^^^^^^^^^^

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``title``                            |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``authors``            | ``creator``                          |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``image``                            |                                        |
+------------------------+--------------------------------------+----------------------------------------+


Visserijmuseum Zoutkamp index
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


TextielMuseum
-------------

This dataset contains images  from the `TextielMuseum <http://www.textielmuseum/>`_.
Content is harvested by using the `Adlib API <http://api.adlibsoft.com/site/>`_.

Combined index
^^^^^^^^^^^^^^

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``title``                            |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``authors``            | ``creator``                          |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``reproduction.identifier_url``      | The source field is part of the URL.   |
+------------------------+--------------------------------------+----------------------------------------+


TextielMuseum index
^^^^^^^^^^^^^^^^^^^


Royal Library - ByvanckB
------------------------

This dataset contains images from the Royal Library's `ByvanckB set <http://manuscripts.kb.nl/>`_.
Content is harvested by using the `OAI-PMH feed <http://services.kb.nl/mdo/oai>`_.
The OCD implementation uses the 'dcx' data format.

Combined index
^^^^^^^^^^^^^^

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``dc:title``                         |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``description``        | ``dc:abstract``                      |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``date``               | ``dc:date``                          | Mostly only year information. the (c.) |
|                        |                                      | is stripped, then parsed.              |
|                        |                                      | Therefor, ``date_granularity`` is      |
|                        |                                      | always 4 when it was properly parsed   |
+------------------------+--------------------------------------+----------------------------------------+
| ``authors``            | ``dc:creator``                       |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``dcx:illustration``                 |                                        |
+------------------------+--------------------------------------+----------------------------------------+

Royal Library - ByvanckB index
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Tropenmuseum
------------

This dataset contains images from the `Tropenmusem <http://collectie.tropenmuseum.nl/Default.aspx>`_.
The Wikimedia Commons API is used to get the dataset.

Combined index
^^^^^^^^^^^^^^

+------------------------+--------------------------------------+----------------------------------------+
| Combined index field   | Source field(s)                      | Comment                                |
+========================+======================================+========================================+
| ``title``              | ``file/name``                        |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``date``               | ``file/date``                        |                                        |
+------------------------+--------------------------------------+----------------------------------------+
| ``description``        | ``description/language``             | Only the dexcription with ``lang="nl"``|
|                        |                                      | is included. All HTML tags are removed.|
+------------------------+--------------------------------------+----------------------------------------+
| ``media_urls``         | ``file/name``                        |                                        |
+------------------------+--------------------------------------+----------------------------------------+

Tropenmuseum index
^^^^^^^^^^^^^^^^^^


