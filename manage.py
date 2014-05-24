#!/usr/bin/env python

import json
from glob import glob

import click
from werkzeug.serving import run_simple

from ocd_backend.es import elasticsearch as es
from ocd_backend.pipeline import setup_pipeline
from ocd_backend.settings import SOURCES_CONFIG_FILE, DEFAULT_INDEX_PREFIX
from ocd_backend.utils.misc import load_sources_config
from ocd_frontend.wsgi import application


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
    """Create all indexes for which a mapping- and settingsfile is avialble.

    It is assumed that mappings in the specified directory follow the
    following nameing convention: "ocd_mapping_{SOURCE_NAME}.json".
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


if __name__ == '__main__':
    cli()
