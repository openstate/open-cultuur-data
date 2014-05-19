Open Cultuur Data API backend install notes
-------------------------------------------

This is a quick install guide written for Lex to get him started with running the Open Cultuur Data (OCD) backend. More comprehensive documentation still needs to be written and added to OCD's documentation (currently located at http://dump.dispectu.com/ocd/).

Pre-requisites
==============

- Redis
- Elasticsearch >= 1.1
- Python(-dev) 2.7
- liblxml
- libxslt
- pip
- virtualenv (optional)

Installation
============

1. Install redis::

   $ sudo add-apt-repository ppa:rwky/redis
   $ sudo apt-get update
   $ sudo apt-get install redis-server

2. Install Elasticsearch::

   $ wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.1.1.deb
   $ sudo dpkg -i elasticsearch-1.1.1.deb

3. Install liblxml, libxslt and python-dev::

   $ sudo apt-get install libxml2-dev libxslt1-dev python-dev

4. Install pip and virtualenv::

   $ sudo easy_install pip

5. Create an OCD virtualenv and source it::

   $ virtualenv ocd
   $ source ocd/bin/activate

6. Clone the OCD git repository and install the required Python packages::

   $ git clone https://github.com/openstate/open-cultuur-data.git
   $ cd open-cultuur-data/
   $ pip install -r requirements.txt


Running an OCD extractor
========================

1. First, add the OCD template to the running Elasticsearch instance::

   $ ./manage.py elasticsearch put_template

2. Make the necessary changes to the 'sources' settings file (``ocd_backend/sources.json``). For example, fill out your API key for retrieving data from the Rijksmuseum.

3. Start the extraction process::

   $ ./manage.py extract start openbeelden

   You can get an overview of the available sources by running ``./manage.py extract list_sources``.

4. Simultaneously start a worker processes::

   $ celery --app=ocd_backend:celery_app worker --loglevel=info --concurrency=2

