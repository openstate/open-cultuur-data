from celery import chain, chord, group
from datetime import datetime
from elasticsearch.exceptions import NotFoundError

from ocd_backend.es import elasticsearch as es
from ocd_backend import settings
from ocd_backend.tasks import UpdateAlias
from ocd_backend.utils.misc import load_object
from .exceptions import ConfigurationError


def setup_pipeline(source_definition):
    # index_name is an alias of the current version of the index
    index_alias = '{prefix}_{index_name}'.format(
        prefix=settings.DEFAULT_INDEX_PREFIX,
        index_name=source_definition.get('index_name')
    )

    if not es.indices.exists(index_alias):
        index_name = '{index_alias}_{now}'.format(index_alias=index_alias,
                                                  now=datetime.utcnow()
                                                  .strftime('%Y%m%d%H%M%S'))

        es.indices.create(index_name)
        es.indices.put_alias(name=index_alias, index=index_name)

    # Find the current index name behind the alias specified in the config
    try:
        current_index_aliases = es.indices.get_alias(name=index_alias)
    except NotFoundError:
        raise ConfigurationError('Index with alias "{index_alias}" does not exi'
                                 'st'.format(index_alias=index_alias))

    current_index_name = current_index_aliases.keys()[0]
    new_index_name = '{index_alias}_{now}'.format(
        index_alias=index_alias, now=datetime.utcnow().strftime('%Y%m%d%H%M%S')
    )

    extractor = load_object(source_definition['extractor'])(source_definition)
    transformer = load_object(source_definition['transformer'])()
    loader = load_object(source_definition['loader'])()


    # jobs = group(chain(transformer.s(*item, source_definition=source_definition), loader.s(source_definition=source_definition, index_name=new_index_name)) for item in extractor.run())
    # jobs = [chain(transformer.s(*item, source_definition=source_definition), loader.s(source_definition=source_definition, index_name=new_index_name)) for item in extractor.run()]
    # print jobs
    update_alias = UpdateAlias()

    tasks = []
    for item in extractor.run():
        tasks.append(chain(transformer.si(*item, source_definition=source_definition), loader.s(source_definition=source_definition, index_name=new_index_name)))

    chord(group(tasks))(update_alias.s(current_index_name=current_index_name,
                                       new_index_name=new_index_name,
                                       alias=index_alias))
