Open Cultuur Data API install notes
###################################

Using Docker
============

The Open Cultuur Data API is easily installed using `Docker Compose<https://docs.docker.com/compose/install/>`_.

1. Clone the OCD git repository::

   git clone https://github.com/openstate/open-cultuur-data.git
   cd open-cultuur-data/docker

(optional) If you're developing then uncomment the ``Development`` and comment the ``Production`` sections in ``docker/nginx/conf.d/default.conf`` and ``conf/supervisor.conf``. You will then use Flask's development webserver instead of uWSGI, which is useful because changes to the code are automatically reloaded.

2. Build and run the image using::

   sudo docker-compose up -d

Running an OCD extractor
========================

1. First, add the OCD template to the running Elasticsearch instance::

   ./manage.py elasticsearch put_template

2. Make the necessary changes to the 'sources' settings file (``ocd_backend/sources.json``). For example, fill out your API key for retrieving data from the Rijksmuseum.

3. Start the extraction process::

   ./manage.py extract start openbeelden

You can get an overview of the available sources by running ``./manage.py extract list_sources``.

Backup and restore
==================

Some commands on how to [backup and restore Elasticsearch indices](https://www.elastic.co/guide/en/elasticsearch/reference/1.4/modules-snapshots.html#_shared_file_system_repository).

The following commands are assumed to be executed in the Docker container. You can enter the container using this command (exit it using ``CTRL+d``)::

   sudo docker exec -it docker_c-ocd-app_1 bash

# Create a new backup location in the root directory of the OCD repository (do this on the machine which should be backupped AND the machine where you want to restore the backup) and make sure Elasticsearch can write to it, e.g.::

   mkdir backups
   chown 102 backups
   curl -XPUT 'http://localhost:9200/_snapshot/my_backup' -d '{"type": "fs", "settings": {"location": "/opt/ocd/backups"}}'

# Save all indices/cluster with a snapshot::

   curl -XPUT "localhost:9200/_snapshot/my_backup/ocd_backup"

# Copy the ``backups`` directory containing the snapshot into the ``open-cultuur-data`` directory on the other machine (on this other machine, make sure you created a backup location as described above). Restore the permissions to make sure that it is still reacheable by Elasticsearch::

   chown 102 backups

# Close any indices with the same name which are already present on the new machine. On a new install these are ``ocd_resolver`` and ``ocd_usage_logs``::

   curl -XPOST 'localhost:9200/ocd_resolver/_close'
   curl -XPOST 'localhost:9200/ocd_usage_logs/_close'


# Restore the snapshot::

   curl -XPOST "localhost:9200/_snapshot/my_backup/ocd_backup/_restore"
