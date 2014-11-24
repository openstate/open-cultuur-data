Backup and restore
==================
The OpenCultuurData (OCD) API provides a uniform interface to cultural heritage data from a wide variety of resources and collections, with a wide range of technical resources at their disposal. Depending on the resource and collection, loading data with the :ref:`ETL pipeline <dev_etl>` can be a long and arduous task, especially during development, where a lot of quick iterations between modifying code and reloading the data is desirable. To limit the strain developers can accidentally put on the resources of data providers, and to simplify and accelerate development, the :ref:`OCD command line interface <dev_cli>` (CLI) provides a set of commands to download a dump of a collection, and load that collection quickly into your own OCD API instance. Additionally, it provides a command to create a backup of your own index, that you can easily share with others, for instance when you have performed some additional analysis on some collections.

Obtain a backup
---------------
To load a backup into your own API instance, you first need to download an existing backup. OpenState hosts the latest dumps at http://dumps.opencultuurdata.nl, which are updated regularly. Use the following command to download a dump to your local machine::

    (ocd-env)$ ./manage.py dumps download
    1) ocd_openbeelden
    2) ocd_rijksmuseum
    Which dumps should be downloaded? Please provide the number(s) corresponding to the dumps that should be downloaded: 1,2

In this example, there are two dumps available at the API instance we want to obtain data from (this can be any OCD API instance, such as your own, or the one hosted by OpenState). You are prompted for a comma-separated list of values, so choose the dumps you wish to download. If you want to download both::

    Creating path "/vagrant/local_dumps/ocd_openbeelden"
    Downloading ocd_openbeelden  [####################################]  100%
    Creating path "/vagrant/local_dumps/ocd_rijksmuseum"
    Downloading ocd_rijksmuseum  [############################--------]   72%  00:00:02

It will download the files to your local machine (the CLI provides options to override where to download the files to). Note that the CLI will perform checksum validation for each download, so if you already have the correct file, it will not download the dump again::

    (ocd-env)$ ./manage.py dumps download
    1) ocd_openbeelden
    2) ocd_rijksmuseum
    Which dumps should be downloaded? Please provide the number(s) corresponding to the dumps that should be downloaded: 2
    This file is already downloaded (/vagrant/local_dumps/ocd_rijksmuseum/ocd_rijksmuseum_201411111436.sha1)

Restoring from a backup
-----------------------
Once you have a dump, you can create an index from it. If you're not running this on the Vagrant development box, you'll probably need to PUT the OCD mapping and settings to the Elasticsearch instance powering your local API instance. Execute the following CLI command::

    (ocd-env)$ ./manage.py elasticsearch put_template
    Putting ES template: es_mappings/ocd_template.json

This will apply the proper settings to each index which names is prefixed with ``ocd_*``.

Make sure you have the Celery worker running in a separate screen, as it will take care of extracting, transforming and loading data from the dump into your API instance::

    (ocd-env)$ celery --app=ocd_backend:celery_app worker --loglevel=info --concurrency=2

Executing the following command will prompt you with a list of dumps you have available locally, and will set up a ETL-pipeline for the dump indicated. I will load the dump of the :ref:`OpenBeelden collection <data_openbeelden>`::

    (ocd-env)$ ./manage.py dumps load
    1) /vagrant/local_dumps/ocd_openbeelden/ocd_openbeelden_201411111421.gz
    2) /vagrant/local_dumps/ocd_rijksmuseum/ocd_rijksmuseum_201411111436.gz
    Choose one of the dumps listed above: 1
    {'extractor': 'ocd_backend.extractors.staticfile.StaticJSONDumpExtractor', 'transformer': 'ocd_backend.transformers.BaseTransformer', 'dump_path': '/vagrant/local_dumps/ocd_openbeelden/ocd_openbeelden_201411111421.gz', 'loader': 'ocd_backend.loaders.ElasticsearchLoader', 'item': 'ocd_backend.items.LocalDumpItem', 'id': 'ocd_openbeelden'}
    Loading /vagrant/local_dumps/ocd_openbeelden/ocd_openbeelden_201411111421.gz  [####################################]
    Queued items from /vagrant/local_dumps/ocd_openbeelden/ocd_openbeelden_201411111421.gz. Please make sure your Celery workers are running, so the loaded items are processed.

This will show you the pipeline configuration it creates, and queue all items that are contained within the dump. If you check your Celery worker, you should see it hard at work restoring the index from the dump.

Creating your own dumps/backups
-------------------------------
Now that we have an index in our own API instance, we can query, analyze and enrich it however we see fit. For instance, you could create some classifier that finds funny pictures in your index, and adds a "funny-ness" score to each item in the index. You probably want to backup this data, and maybe make this data available to other people as well. The CLI provides an interface for creating backups, which will automatically be made available on your own API instance as well. Running the following command will list all the indices available on the API instance the command is run; as we are continuing the running example, the ``ocd_openbeelden`` index is available::

    (ocd-env)$ ./manage.py dumps create
    ocd_openbeelden (4748 docs, 16.8mb)
    Name of index to dump: ocd_openbeelden
    [####################################]  100%
    Generating checksum
    Created dump "ocd_openbeelden_20141111155119.gz" (checksum f007a4fc72e92ac6127f1a61291fd0bb373813d9)
    Created symlink "ocd_openbeelden_latest.gz" to "/vagrant/dumps/ocd_openbeelden/ocd_openbeelden_20141111155119.gz"
    Created symlink "ocd_openbeelden_latest.sha1" to "/vagrant/dumps/ocd_openbeelden/ocd_openbeelden_20141111155119.sha1"
