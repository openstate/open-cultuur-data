#!/usr/bin/env python

from datetime import datetime
import json
from glob import glob
import gzip
from hashlib import sha1
import os
import requests

import click
from elasticsearch import helpers as es_helpers
from werkzeug.serving import run_simple

from ocd_backend.es import elasticsearch as es
from ocd_backend.pipeline import setup_pipeline
from ocd_backend.settings import SOURCES_CONFIG_FILE, DEFAULT_INDEX_PREFIX
from ocd_backend.utils.misc import load_sources_config
from ocd_frontend.settings import BACKUP_DIR, API_URL
from ocd_frontend.wsgi import application


def _create_path(path):
    if not os.path.exists(path):
        click.secho('Creating path "%s"' % path, fg='green')
        os.makedirs(path)

    return path

def _checksum_file(target):
    """
    Compute sha1 checksum of a file. As some files could potentially be huge,
    iterate in blocks of 32kb to keep memory overhead to a minimum

    :param target: path to file to compute checksum on
    :return: SHA1 checksum of file
    """
    checksum = sha1()
    # 'rb': don't convert input to text buffer
    with open(target, 'rb') as f:
        # Read in chunks; must be a multiple of 128 bytes
        for chunk in iter(lambda: f.read(32768), b''):
            checksum.update(chunk)
    return checksum.hexdigest()


@click.group()
@click.version_option()
def cli():
    """Open Cultuur Data"""


@cli.group()
def elasticsearch():
    """Manage Elasticsearch"""


@elasticsearch.command('put_template')
@click.option('--template_file', default='es_mappings/ocd_template.json',
              type=click.File('rb'), help='Path to JSON file containing the template.')
def es_put_template(template_file):
    """Put a template."""
    click.echo('Putting ES template: %s' % template_file.name)

    template = json.load(template_file)
    template_file.close()

    es.indices.put_template('ocd_template', template)


@elasticsearch.command('put_mapping')
@click.argument('index_name')
@click.argument('mapping_file', type=click.File('rb'))
def es_put_mapping(index_name, mapping_file):
    """Put a mapping for a specified index."""
    click.echo('Putting ES mapping %s for index %s'
               % (mapping_file.name, index_name))

    mapping = json.load(mapping_file)
    mapping_file.close()

    es.indices.put_mapping(index=index_name, body=mapping)


@elasticsearch.command('create_indexes')
@click.argument('mapping_dir', type=click.Path(exists=True, resolve_path=True))
def create_indexes(mapping_dir):
    """Create all indexes for which a mapping- and settingsfile is available.

    It is assumed that mappings in the specified directory follow the
    following naming convention: "ocd_mapping_{SOURCE_NAME}.json".
    For example: "ocd_mapping_rijksmuseum.json".
    """
    click.echo('Creating indexes for ES mappings in %s' % (mapping_dir))

    for mapping_file_path in glob('%s/ocd_mapping_*.json' % mapping_dir):
        # Extract the index name from the filename
        index_name = '%s_%s' % (DEFAULT_INDEX_PREFIX, mapping_file_path.split('.')[0].split('_')[-1])

        click.echo('Creating ES index %s' % index_name)

        mapping_file = open(mapping_file_path, 'rb')
        mapping = json.load(mapping_file)
        mapping_file.close()

        es.indices.create(index=index_name, body=mapping)


@elasticsearch.command('delete_indexes')
def delete_indexes():
    """Delete all Open Cultuur Data indices."""
    index_glob = '%s_*' % DEFAULT_INDEX_PREFIX
    indices = es.indices.status(index=index_glob, human=True)

    click.echo('Open Cultuur Data indices:')
    for index, stats in indices['indices'].iteritems():
        click.echo('- %s (%s docs, %s)' % (index, stats['docs']['num_docs'],
                                           stats['index']['size']))
    if click.confirm('Are you sure you want to delete the above indices?'):
        es.indices.delete(index=index_glob)
        es.indices.delete_template('ocd_template')


@elasticsearch.command('available_indices')
def available_indices():
    """
    List available indices
    """
    available = []
    indices = es.cat.indices().strip().split('\n')
    for index in indices:
        index = index.split()
        if u'resolver' not in index[1] and u'combined_index' not in index[1]:
            click.secho('%s (%s docs, %s)' % (index[1], index[4], index[6]),
                        fg='green')
            available.append(index[1])

    return available


@cli.group()
def extract():
    """Extraction pipeline"""


@extract.command('list_sources')
@click.option('--sources_config', default=None, type=click.File('rb'))
def extract_list_sources(sources_config):
    """Show a list of available sources."""
    if not sources_config:
        sources_config = SOURCES_CONFIG_FILE
    sources = load_sources_config(sources_config)

    click.echo('Available sources:')
    for source in sources:
        click.echo(' - %s' % source['id'])


@extract.command('start')
@click.option('--sources_config', default=None, type=click.File('rb'))
@click.argument('source_id')
def extract_start(source_id, sources_config):
    """Start extraction for a specified source."""
    if not sources_config:
        sources_config = SOURCES_CONFIG_FILE
    sources = load_sources_config(sources_config)

    # Find the requested source defenition in the list of available sources
    source = None
    for candidate_source in sources:
        if candidate_source['id'] == source_id:
            source = candidate_source
            continue

    # Without a config we can't do anything, notify the user and exit
    if not source:
        click.echo('Error: unable to find source with id "%s" in sources '
                   'config' % source_id)
        return

    setup_pipeline(source)


@cli.group()
def frontend():
    """Front-end API"""


@frontend.command('runserver')
@click.argument('host', default='0.0.0.0')
@click.argument('port', default=5000, type=int)
def frontend_runserver(host, port):
    run_simple(host, port, application, use_reloader=True, use_debugger=True)


@cli.group()
def backup():
    """Backup and restore"""


@backup.command('create')
@click.option('--index', default=None)
@click.pass_context
def create_backup(ctx, index):
    """
    Create a backup of an index. If you don't provide an ``--index`` option,
    you will be prompted with a list of available index names. Backups are
    stored as a gzipped txt file in ``settings.BACKUP_DIR/<index_name>/<
    timestamp>_<index-name>.backup.gz``, and a symlink ``latest.backup.gz`` is
    created, pointing to the last created backup.

    :param ctx: Click context, so we can issue other management commands
    :param index: name of the index you want to create a backup for
    """
    if not index:
        available_idxs = ctx.invoke(available_indices)
        index = click.prompt('Name of index to backup')

        if index not in available_idxs:
            click.secho('"%s" is not an available index' % index, fg='red')
            return

    match_all = {'query': {'match_all': {}}}

    total_docs = es.count(index=index).get('count')

    path = _create_path(path=os.path.join(BACKUP_DIR, index))
    backup_name = '%(index_name)s_%(timestamp)s.backup.gz' % {
        'index_name': index,
        'timestamp': datetime.now().strftime('%Y%m%d%H%M%S')
    }
    new_backup = os.path.join(path, backup_name)

    with gzip.open(new_backup, 'wb') as g:
        with click.progressbar(es_helpers.scan(es, query=match_all, scroll='1m',
                                               index=index),
                               length=total_docs) as documents:
            for doc in documents:
                g.write('%s\n' % json.dumps(doc))

    click.secho('Generating checksum', fg='green')
    checksum = _checksum_file(new_backup)

    with open(os.path.join(BACKUP_DIR, index, '%s.sha1' % backup_name.split('.')[0]), 'w') as f:
        f.write(checksum)

    click.secho('Created backup "%s" (checksum %s)' % (backup_name, checksum),
                fg='green')


    latest = os.path.join(path, '%s_latest.backup.gz' % index)
    try:
        os.unlink(latest)
    except OSError:
        click.secho('First time creating backup, skipping unlinking',
                    fg='yellow')
    os.symlink(new_backup, latest)

    click.secho('Created symlink "latest.backup.gz" to "%s"' % new_backup,
                fg='green')


@backup.command('list')
@click.option('--api-url', default=API_URL)
def list_backups(api_url):
    """
    List available backups of API instance at ``api_address``.

    :param api_address: URL of API location
    """
    url = '{url}/backups'.format(url=api_url)

    try:
        r = requests.get(url)
    except:
        click.secho('No OCD API instance with backups available at {url}'
                    .format(url=url), fg='red')
        return

    if not r.ok:
        click.secho('Request on {url} failed'.format(url=url), fg='red')

    backups = r.json().get('backups', {})
    for index in backups:
        click.secho(index, fg='green')
        for backup in sorted(backups.get(index, []), reverse=True):
            click.secho('\t{backup}'.format(backup=backup), fg='green')


# @backup.command('download')
# @click.option('--api-url', default=API_URL)
# @click.option('--destination', '-d', default=BACKUP_DIR)
# @click.option('--collections', '-c', multiple=True)
# @click.option('--all-collections', '-a', is_flag=True, expose_value=True)
# @click.pass_context
# def download(ctx, api_url, destination, collections, all_collections):
#     if all_collections:
#         url = '{api_url}/'
#         try:
#             r = requests.get()
#

if __name__ == '__main__':
    cli()
