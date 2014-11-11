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
from ocd_frontend.settings import DUMPS_DIR, API_URL, DUMP_URL, LOCAL_DUMPS_DIR
from ocd_frontend.wsgi import application


class MultiIntRange(click.ParamType):
    """
    A parameter that takes a comma-separated list of integers, and validates
    that the list actually contains integers, within a given range. Used for
    validation of multiple select options in the CLI.
    """
    name = 'multiple integers in a range'

    def __init__(self, min=None, max=None, clamp=False):
        self.min = min
        self.max = max
        self.clamp = clamp

    def convert(self, value, param, ctx):
        v = value.strip().split(',')
        try:
            v = [int(v) for v in v]
        except ValueError:
            self.fail(click.style('{} may only contain integers'.format(value),
                                  fg='red'), param, ctx)

        minv, maxv = min(v), max(v)

        if self.clamp:
            if self.min is not None and minv < self.min:
                return self.min
            if self.max is not None and maxv > self.max:
                return self.max

        if self.min is not None and minv < self.min or self.max is \
            not None and maxv > self.max:
            self.fail(click.style('{} contains values outside the range of '
                                  '{} to {}.'.format(value, self.min, self.max),
                                  fg='red'), param, ctx)

        return v

    def __repr__(self):
        return 'MultiIntRange ({}, {})'.format(self.min, self.max)


def _create_path(path):
    if not os.path.exists(path):
        click.secho('Creating path "%s"' % path, fg='green')
        os.makedirs(path)

    return path


def _checksum_file(target):
    """
    Compute sha1 checksum of a file. As some files could potentially be huge,
    iterate in blocks of 32kb to keep memory overhead to a minimum.

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


def _write_chunks(chunks, f):
    """
    Write chunks (iterable) of a downloading file to filehandler f
    :param chunks: iterable containing chunks to write to disk
    :param f: open, writable filehandler
    """
    for chunk in chunks:
        # Filter out keep-alive chunks
        if chunk:
            f.write(chunk)
            f.flush()


def _download_dump(index, dump_name=None, target_dir=DUMPS_DIR):
    """
    Download a Gzipped dump of a OpenCultuurData collection to disk. Compares
    the SHA1 checksum of the dump with the dump files already available
    locally, and skips downloading if the file is already available.

    :param index: name of the index to get a dump of
    :param dump_name: Optionally provide a name to download a specific dump
                        file. Defaults to downloading the latest dump.
    :param target_dir: Directory to download the dump files to. A directory
                       per index is created in the target directory, and per
                       dump file a checksum and a dump file will be created.
    :return: Path to downloaded dump
    """
    if not dump_name:
        # Pick the latest dump file if no other is specified
        dump_name = '{index}_latest'.format(index=index)

    # Make sure the directory exists
    _create_path(os.path.join(target_dir, index))

    # First, get the SHA1 checksum of the file we intend to download
    r = requests.get('{dump_url}/{index}/{dump_name}.sha1'.format(
        dump_url=DUMP_URL, index=index, dump_name=dump_name))

    checksum = r.content

    # Compare checksums of already downloaded files with the checksum of the
    # file we are trying to download
    for c in glob('{}/*.sha1'.format(os.path.join(target_dir, index))):
        # latest is a symlink
        if 'latest' in c:
            continue
        with open(c, 'r') as f:
            if checksum == f.read():
                click.secho('This file is already downloaded ({})'.format(c),
                            fg='yellow')
                return

    # Construct name of local file
    filepath = os.path.join(target_dir, index, '{}_{}'.format(
        dump_name.replace('_latest', ''),
        datetime.now().strftime('%Y%m%d%H%S'))
    )

    # Get and write dump to disk (iteratively, as dumps could get rather big)
    r = requests.get('{dump_url}/{index}/{dump_name}.gz'.format(
        dump_url=DUMP_URL, index=index, dump_name=dump_name), stream=True)

    content_length = r.headers.get('content-length', False)

    with open('{}.gz'.format(filepath), 'wb') as f:
        if content_length:
            content_length = int(content_length)
            with click.progressbar(r.iter_content(chunk_size=1024),
                                   length=content_length / 1024,
                                   label=click.style(
                                           'Downloading {}'.format(index),
                                           fg='green'
                                   )) as chunks:
                _write_chunks(chunks, f)
        else:
            _write_chunks(r.iter_content(chunk_size=1024), f)

    # Compare checksum of new file with the one on the server in order to make
    # sure everything went OK
    checksum_new_file = _checksum_file('{}.gz'.format(filepath))
    if checksum != checksum_new_file:
        click.secho('Something went wrong during downloading (checksums are not'
                    ' equal), removing file', fg='red')
        os.remove('{}.gz'.format(filepath))
        return

    with open('{}.sha1'.format(filepath), 'w') as f:
        f.write(checksum)

    return '{}.gz'.format(filepath)


def _process_choices(val):
    print val
    return val


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

    # Find the requested source definition in the list of available sources
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
def dumps():
    """Create dumps of indices for export"""


@dumps.command('create')
@click.option('--index', default=None)
@click.pass_context
def create_dump(ctx, index):
    """
    Create a dump of an index. If you don't provide an ``--index`` option,
    you will be prompted with a list of available index names. Dumps are
    stored as a gzipped txt file in ``settings.DUMPS_DIR/<index_name>/<
    timestamp>_<index-name>.gz``, and a symlink ``<index-name>_latest.gz`` is
    created, pointing to the last created dump.

    :param ctx: Click context, so we can issue other management commands
    :param index: name of the index you want to create a dump for
    """
    if not index:
        available_idxs = ctx.invoke(available_indices)
        index = click.prompt('Name of index to dump')

        if index not in available_idxs:
            click.secho('"%s" is not an available index' % index, fg='red')
            return

    match_all = {'query': {'match_all': {}}}

    total_docs = es.count(index=index).get('count')

    path = _create_path(path=os.path.join(DUMPS_DIR, index))
    dump_name = '%(index_name)s_%(timestamp)s.gz' % {
        'index_name': index,
        'timestamp': datetime.now().strftime('%Y%m%d%H%M%S')
    }
    new_dump = os.path.join(path, dump_name)

    with gzip.open(new_dump, 'wb') as g:
        with click.progressbar(es_helpers.scan(es, query=match_all, scroll='1m',
                                               index=index),
                               length=total_docs) as documents:
            for doc in documents:
                g.write('%s\n' % json.dumps(doc))

    click.secho('Generating checksum', fg='green')
    checksum = _checksum_file(new_dump)
    checksum_path = os.path.join(DUMPS_DIR, index, '%s.sha1' % dump_name.split('.')[0])

    with open(checksum_path, 'w') as f:
        f.write(checksum)

    click.secho('Created dump "%s" (checksum %s)' % (dump_name, checksum),
                fg='green')


    latest = os.path.join(path, '%s_latest.gz' % index)
    try:
        os.unlink(latest)
    except OSError:
        click.secho('First time creating dump, skipping unlinking',
                    fg='yellow')
    os.symlink(new_dump, latest)
    click.secho('Created symlink "%s_latest.gz" to "%s"' % (index, new_dump),
                fg='green')

    latest_checksum = os.path.join(os.path.dirname(checksum_path), '%s_latest.sha1' % index)
    try:
        os.unlink(latest_checksum)
    except OSError:
        click.secho('First time creating dump, skipping unlinking checksum',
                    fg='yellow')
    os.symlink(checksum_path, latest_checksum)
    click.secho('Created symlink "%s_latest.sha1" to "%s"' % (index, checksum_path),
                fg='green')


@dumps.command('list')
@click.option('--api-url', default=API_URL)
def list_dumps(api_url):
    """
    List available dumps of API instance at ``api_address``.

    :param api_address: URL of API location
    """
    url = '{url}/dumps'.format(url=api_url)

    try:
        r = requests.get(url)
    except:
        click.secho('No OCD API instance with dumps available at {url}'
                    .format(url=url), fg='red')
        return

    if not r.ok:
        click.secho('Request on {url} failed'.format(url=url), fg='red')

    dumps = r.json().get('dumps', {})
    for index in dumps:
        click.secho(index, fg='green')
        for dump in sorted(dumps.get(index, []), reverse=True):
            click.secho('\t{dump}'.format(dump=dump), fg='green')


@dumps.command('download')
@click.option('--api-url', default=API_URL, help='URL to API instance to fetch '
                                                 'dumps from.')
@click.option('--dump-url', default=DUMP_URL, help='URL where dumps are hosted,')
@click.option('--destination', '-d', default=LOCAL_DUMPS_DIR,
              help='Directory to download dumps to.')
@click.option('--collections', '-c', multiple=True)
@click.option('--all-collections', '-a', is_flag=True, expose_value=True,
              help='Download latest version of all collections available')
def download_dumps(api_url, dump_url, destination, collections, all_collections):
    """
    Download dumps of OCD collections to your machine, for easy ingestion.

    :param api_url: URL to API instance to fetch dumps from
    :param dump_url: Base URL where dumps are hosted
    :param destination: path to local directory where dumps should be stored
    :param collections: Names of collections to fetch dumps for.
    :param all_collections: If this flag is set, download all available dumps
    """
    url = '{url}/dumps'.format(url=api_url)
    try:
        r = requests.get(url)
    except:
        click.secho('Could not connect to API', fg='red')
        return

    dumps = [(i+1, index) for i, index in enumerate(r.json().get('dumps'))]
    dump_mapping = dict(dumps)
    available_collections = dump_mapping.values()

    if all_collections:
        # Download all the things
        for i, index in dumps:
            _download_dump(index, target_dir=destination)
        return

    if not collections:
        for i, index in dumps:
            click.secho('{i}) {index}'.format(i=i, index=index), fg='yellow')

        dumps = click.prompt('Which dumps should be downloaded? Please provide '
                             'the number(s) corresponding to the dumps that sho'
                             'uld be downloaded',
                             type=MultiIntRange(*range(dumps[0][0],
                                                       dumps[-1][0] + 1)))
        for d in dumps:
            _download_dump(dump_mapping[d], target_dir=destination)

        return

    for collection in collections:
        if collection not in available_collections:
            click.secho('"{}" is not available as a dump, skipping'.format(collection),
                        fg='red')
            continue
        _download_dump(collection, target_dir=destination)


@dumps.command('load')
@click.option('--collection', '-c', help='Path to dump of collection to load',
              default=None, type=click.Path(exists=True))
@click.option('--collection-name', '-n', help='An index will be created with th'
                                              'is name. If left empty, collecti'
                                              'on name will be derived from dum'
                                              'p name.', default=None)
def load_dump(collection, collection_name):
    available_dumps = glob(os.path.join(LOCAL_DUMPS_DIR, '*/*.gz'))
    if not collection:
        choices = []
        for i, dump in enumerate(available_dumps):
            choices.append(unicode(i+1))
            click.secho('{i}) {dump}'.format(i=i+1, dump=dump), fg='green')
        dump_idx = click.prompt('Choose one of the dumps listed above',
                                type=click.Choice(choices))
        collection = available_dumps[int(dump_idx) - 1]

    collection = os.path.abspath(collection)

    if not collection_name:
        collection_name = '_'.join(collection.split('/')[-1].split('.')[0].split('_')[:2])

    source_definition = {
        'id': collection_name,
        'extractor': 'ocd_backend.extractors.staticfile.StaticJSONDumpExtractor',
        'transformer': 'ocd_backend.transformers.BaseTransformer',
        'loader': 'ocd_backend.loaders.ElasticsearchLoader',
        'item': 'ocd_backend.items.LocalDumpItem',
        'dump_path': collection
    }

    click.secho(str(source_definition), fg='yellow')

    setup_pipeline(source_definition)
    click.secho('Queued items from {}. Please make sure your Celery workers are'
                ' running, so the loaded items are processed.'.format(collection),
                fg='green')


if __name__ == '__main__':
    cli()
