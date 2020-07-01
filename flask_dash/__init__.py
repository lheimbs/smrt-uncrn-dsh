"""Initialize Flask app."""
from flask import Flask
# from extra.get_config import get_config


def register_blueprints(app):
    """ Register all app Blueprints """
    from .admin import admin
    app.register_blueprints(admin.admin_bp)


def create_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)

    from config import init_config
    init_config(app)

    from .models import init_db
    init_db(app)

    from .auth import init_login
    init_login(app)

    # from .admin import init_admin
    # init_admin(app)

    with app.app_context(), app.test_request_context():
        # Import Flask routes
        from flask_dash import routes           # noqa: F401

        from .admin import admin_bp, admin      # noqa: F401
        app.register_blueprint(admin_bp)

        # Compile CSS
        from flask_dash.assets import compile_assets
        compile_assets(app)

        # Import Dash application
        from flask_dash.dash_apps.dashboard import create_dashboard
        create_dashboard(app)

        from flask_dash.dash_apps.graph import create_graph
        create_graph(app)


        return app
