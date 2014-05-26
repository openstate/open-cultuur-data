Open Cultuur Data API install notes
###################################

Using Vagrant
=============

Using `Vagrant <http://www.vagrantup.com/>`_ is by far the easiest way to spin up a development environment and get started with contributing to the Open Cultuur Data API.

1. Clone the OCD git repository::

   $ git clone https://github.com/openstate/open-cultuur-data.git
   $ cd open-cultuur-data/

2. Select and link the correct ``Vagrantfile`` (depending on the Vagrant provider you use)::

   $ ln -s Vagrantfile.virtualbox Vagrantfile

3. Start the Vagrant box and SSH into it::

   $ vagrant up && vagrant ssh

Vagrant will automatically sync your project directory (the directory with the Vagrantfile) between the host and guest machine. In the guest, the project directory can be found under ``/vagrant``. For more information, see the Vagrant documentation on `Synced Folders <http://docs.vagrantup.com/v2/synced-folders/index.html>`_.

Manual setup
============

Pre-requisites
--------------

- Redis
- Elasticsearch >= 1.1
- Python(-dev) 2.7
- liblxml
- libxslt
- pip
- virtualenv (optional)

Installation
------------

1. Install redis::

   $ sudo add-apt-repository ppa:rwky/redis
   $ sudo apt-get update
   $ sudo apt-get install redis-server
   
2. Install Java (if it isn't already)::
   
   $ sudo apt-get install openjdk-7-jre-headless

3. Install Elasticsearch::
   
   $ wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.2.0.deb
   $ sudo dpkg -i elasticsearch-1.2.0.deb

4. Install liblxml, libxslt and python-dev::

   $ sudo apt-get install libxml2-dev libxslt1-dev python-dev

5. Install pip and virtualenv::

   $ sudo easy_install pip

6. Create an OCD virtualenv and source it::

   $ virtualenv ocd
   $ source ocd/bin/activate

7. Clone the OCD git repository and install the required Python packages::

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
