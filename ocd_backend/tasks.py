from celery import Task

from ocd_backend.es import elasticsearch as es


class UpdateAlias(Task):
    ignore_result = True

    def run(self, *args, **kwargs):
        current_index_name = kwargs.get('current_index_name')
        new_index_name = kwargs.get('new_index_name')
        alias = kwargs.get('alias')

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
