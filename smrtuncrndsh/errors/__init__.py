from flask import render_template


def register_handlers(app):
    if app.config.get('DEBUG') is True:
        app.logger.debug('Skipping error handlers in Debug mode')
        return

    @app.errorhandler(403)
    def forbidden_page(*args, **kwargs):
        # do stuff
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(*args, **kwargs):
        # do stuff
        return render_template("errors/404.html"), 404

    @app.errorhandler(410)
    def page_gone(*args, **kwargs):
        # do stuff
        return render_template("errors/405.html"), 410

    @app.errorhandler(500)
    def server_error_page(*args, **kwargs):
        # do stuff
        return render_template("errors/500.html"), 500
