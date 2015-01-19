from ocd_backend.exceptions import NoChainIDAvailable


class OCDBackendTaskMixin(object):
    """
    Mixin for `Tasks` using the backend, which makes sure the Task cleans up
    bookkeeping that is happening in the result backend to know when all tasks
    have finished.
    """
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self._remove_chain('{}_chains'.format(kwargs.get('run_identifier')),
                           kwargs.get('chain_id'))
        self.AsyncResult(task_id=task_id).forget()

    def _remove_chain(self, run_identifier, value):
        self.backend.remove_value_from_set(run_identifier, value)

        # If we've removed the last value, remove the set key as well
        if self.backend.get_set_cardinality(run_identifier) < 1:
            self.backend.remove(run_identifier)
