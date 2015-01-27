from datetime import datetime
from uuid import uuid4

from elasticsearch.exceptions import NotFoundError

from ocd_backend.es import elasticsearch as es
from ocd_backend import settings, celery_app
from ocd_backend.log import get_source_logger
from ocd_backend.utils.misc import load_object
from ocd_backend.exceptions import ConfigurationError

logger = get_source_logger('pipeline')


def setup_pipeline(source_definition):
    # index_name is an alias of the current version of the index
    index_alias = '{prefix}_{index_name}'.format(
        prefix=settings.DEFAULT_INDEX_PREFIX,
        index_name=source_definition.get('index_name',
                                         source_definition.get('id'))
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

    # Parameters that are passed to each task in the chain
    params = {
        'run_identifier': 'pipeline_{}'.format(uuid4().hex),
        'current_index_name': current_index_name,
        'new_index_name': new_index_name,
        'index_alias': index_alias
    }

    celery_app.backend.set(params['run_identifier'], 'running')
    run_identifier_chains = '{}_chains'.format(params['run_identifier'])

    try:
        for item in extractor.run():
            # Generate an identifier for each chain, and record that in
            # {}_chains, so that we can know for sure when all tasks from an
            # extractor have finished
            params['chain_id']= uuid4().hex
            celery_app.backend.add_value_to_set(set_name=run_identifier_chains,
                                                value=params['chain_id'])
            (transformer.s(*item, source_definition=source_definition, **params)
             | loader.s(source_definition=source_definition, **params)).delay()
    except:
        logger.error('An exception has occured in the "{extractor}" extractor. '
                     'Deleting index "{index}" and setting status of run '
                     'identifier "{run_identifier}" to "error".'
                     .format(index=new_index_name,
                             run_identifier=params['run_identifier'],
                             extractor=source_definition['extractor']))

        celery_app.backend.set(params['run_identifier'], 'error')
        raise

    celery_app.backend.set(params['run_identifier'], 'done')
