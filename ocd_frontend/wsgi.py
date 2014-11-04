from werkzeug.wsgi import DispatcherMiddleware

from ocd_frontend import rest

application = DispatcherMiddleware(rest.create_app(), {
    '/v0': rest.create_app()
})

# For testing purposes, add a route that serves static files from a directory.
# DO NOT USE IN PRODUCTION. Serve static files through your webserver instead.
if application.app.config.get('DEBUG', False):
    from flask import send_from_directory

    @application.app.route('/data/<path:filename>')
    def download_dump(filename):
        return send_from_directory(application.app.config.get('DUMPS_DIR'),
                                   filename, as_attachment=True)
