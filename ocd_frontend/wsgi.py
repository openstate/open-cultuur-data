from werkzeug.wsgi import DispatcherMiddleware

from ocd_frontend import rest, quicksearch

application = DispatcherMiddleware(quicksearch.create_app(), {
    '/v0': rest.create_app()
})
