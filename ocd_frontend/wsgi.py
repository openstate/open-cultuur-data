from werkzeug.wsgi import DispatcherMiddleware

from ocd_frontend import rest

application = DispatcherMiddleware(rest.create_app(), {
    '/api/v0': rest.create_app()
})
