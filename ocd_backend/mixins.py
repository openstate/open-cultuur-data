from ocd_backend import celery_app
from ocd_backend.exceptions import NoChainIDAvailable


class OCDBackendTaskMixin(object):
    """
    Mixin for `Tasks` using the backend, which makes sure the Task cleans up
    bookkeeping that is happening in the result backend to know when all tasks
    have finished.
    """
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if not kwargs.get('chain_id'):
            raise NoChainIDAvailable

        if not kwargs.get('run_identifier'):
            raise NoRunIDAvailable

        celery_app.backend.remove_value_from_set('{}_chains'.format(kwargs.get('run_identifier')), kwargs.get('chain_id'))
        self.AsyncResult(task_id=task_id).forget()
