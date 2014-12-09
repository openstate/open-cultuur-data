from celery import Task

from ocd_backend.es import elasticsearch as es
from ocd_backend.log import get_source_logger


log = get_source_logger('ocd_backend.tasks')


class UpdateAlias(Task):
    ignore_result = True

    def run(self, *args, **kwargs):
        current_index_name = kwargs.get('current_index_name')
        new_index_name = kwargs.get('new_index_name')
        alias = kwargs.get('alias')

        # Results are stored up to 30 minutes by default in the Redis storage
        # backend, but we'll clean up here to limit strain on resources
        for r in args[0]:
            log.debug('Processed item {item_id}; removing tasks ({task_id}, '
                      '{transformer_task_id}) from result backend'
                      .format(item_id=r.get('item_id'),
                              task_id=r.get('task_id'),
                              transformer_task_id=r.get('transformer_task_id')
                )
            )
            self.AsyncResult(task_id=r.get('task_id')).forget()
            self.AsyncResult(task_id=r.get('transformer_task_id')).forget()

        actions = {
            'actions': [
                {'remove': {'index': current_index_name, 'alias': alias}},
                {'add': {'index': new_index_name, 'alias': alias}}
            ]
        }

        # Set alias to new index
        es.indices.update_aliases(body=actions)

        # Remove old index
        es.indices.delete(index=current_index_name)
