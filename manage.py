import json
from glob import glob

import click

from ocd_backend.es import elasticsearch as es
from ocd_backend.settings import SOURCES


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


@elasticsearch.command('put_all_mappings')
@click.argument('mapping_dir', type=click.Path(exists=True, resolve_path=True))
def put_all_mappings(mapping_dir):
    """Put all mappings in a specifc directory.

    It is assumed that mappings in the specified directory follow the
    following nameing convention: "ocd_mapping_{SOURCE_NAME}.json".
    For example: "ocd_mapping_rijksmuseum.json".
    """
    click.echo('Putting ES mappings in %s' % (mapping_dir))

    for mapping_file_path in glob('%s/ocd_mapping_*.json' % mapping_dir):
        # Extract the index name from the filename
        index_name = mapping_file_path.split('.')[0].split('_')[-1]

        click.echo('Putting ES mapping %s for index %s'
                   % (mapping_file_path, index_name))

        mapping_file = open(mapping_file_path, 'rb')
        mapping = json.load(mapping_file)
        mapping_file.close()

        es.indices.put_mapping(index=index_name, body=mapping)


if __name__ == '__main__':
    cli()
