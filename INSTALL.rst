Open Cultuur Data API install notes
###################################

Install
=======

The Open Cultuur Data API is easily installed using `Docker Compose <https://docs.docker.com/compose/install/>`_.

1. Clone the OCD git repository::

   $ git clone https://github.com/openstate/open-cultuur-data.git
   $ cd open-cultuur-data/docker

(optional) If you're developing then uncomment the ``Development`` and comment the ``Production`` sections in ``docker/nginx/conf.d/default.conf`` and ``conf/supervisor.conf``. You will then use Flask's development webserver instead of uWSGI, which is useful because changes to the code are automatically reloaded.
You can also remove the lines ``restart: always`` from ``docker/docker-compose.yml`` otherwise the containers will automatically start when you start your machine.
(optional) In ``docker/docker-compose.yml`` you might want to remove the line containing ``- nginx-load-balancer`` listed in the networks section of the ``c-ocd-nginx`` service as well as the last three lines (shown below) as they are specific to our setup and not needed for general usage::
  nginx-load-balancer:
    external:
      name: docker_nginx-load-balancer

2. Build and run the image using (only use this once unless you want to rebuild stuff)::

   $ sudo docker-compose up -d

On reboots, the docker containers should automatically restart again. If you removed the ``restart: always`` lines from ``docker/docker-compose.yml``, then you can start the containers as follows::

   $ cd open-cultuur-data/docker
   $ sudo docker-compose start

Running an OCD extractor
========================

1. Make the necessary changes to the 'sources' settings file (``ocd_backend/sources.json``). For example, fill out your API key for retrieving data from the Rijksmuseum.

2. Enter the container::

   $ sudo docker exec -it docker_c-ocd-app_1 bash

3. Start the extraction process for a specific source, in this case ``openbeelden``::

   $ ./manage.py extract start openbeelden

You can get an overview of the available sources by running ``./manage.py extract list_sources``.

Useful commands
===============

Restart the OCD API::

   $ cd open-cultuur-data/docker
   $ sudo docker-compose restart

Code that is updated in production can be reloaded by restarting UWSGi as follows::

   $ cd open-cultuur-data
   $ touch uwsgi-touch-reload

List all indices::

   $ sudo docker exec -it docker_c-ocd-app_1 bash
   $ curl 'http://127.0.0.1:9200/_cat/indices?v'

Remove a source, in this case ``collectie_gelderland``::

   $ sudo docker exec -it docker_c-ocd-app_1 bash
   # Delete the source index
   # Find the exact index name using the 'list all indices' commands above, in this case 'ocd_collectie_gelderland_20161208001124'
   $ curl -XDELETE 'http://127.0.0.1:9200/ocd_collectie_gelderland_20161208001124'
   # Delete the source entries from the combined_index, in this case 'collectie_gelderland'
   $ curl -XDELETE 'http://127.0.0.1:9200/ocd_combined_index/item/_query' -d '{"query": {"match": {"meta.source_id": "collectie_gelderland"}}}'

Development
===========

Here are some useful tips for development besides the development instructions in the 'Install' section.

After changing code in the backend, enter the container and kill ``celery`` to reload the code (supervisor will automatically restart ``celery``)::

   $ sudo docker exec -it docker_c-ocd-app_1 bash
   $ kill -9 `ps aux | grep celery | awk '{print $2}'`

Make sure to check ``open-cultuur-data/log/celery.err`` when extracting a new source. This log file will most likely contain useful information if anything goes wrong.

Backup and restore
==================

Some commands on how to `backup and restore Elasticsearch indices <https://www.elastic.co/guide/en/elasticsearch/reference/1.4/modules-snapshots.html#_shared_file_system_repository>`_.

The following commands are assumed to be executed in the Docker container. You can enter the container using this command (exit it using ``CTRL+d``)::

   $ sudo docker exec -it docker_c-ocd-app_1 bash

Create a new backup location in the root directory of the OCD repository (do this on the machine which should be backupped AND the machine where you want to restore the backup) and make sure Elasticsearch can write to it, e.g.::

   $ mkdir backups
   $ chown 102 backups
   $ curl -XPUT 'http://localhost:9200/_snapshot/my_backup' -d '{"type": "fs", "settings": {"location": "/opt/ocd/backups"}}'

Save all indices/cluster with a snapshot::

   $ curl -XPUT "localhost:9200/_snapshot/my_backup/ocd_backup"

Copy the ``backups`` directory containing the snapshot into the ``open-cultuur-data`` directory on the other machine (on this other machine, make sure you created a backup location as described above). Restore the permissions to make sure that it is still reacheable by Elasticsearch::

   $ chown 102 backups

Close any indices with the same name which are already present on the new machine. On a new install these are ``ocd_resolver`` and ``ocd_usage_logs``::

   $ curl -XPOST 'localhost:9200/ocd_resolver/_close'
   $ curl -XPOST 'localhost:9200/ocd_usage_logs/_close'

Restore the snapshot::

   $ curl -XPOST "localhost:9200/_snapshot/my_backup/ocd_backup/_restore"
