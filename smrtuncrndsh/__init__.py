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

    with app.app_context(), app.test_request_context():

        from .admin import admin_bp, users, activation          # noqa: F401
        app.register_blueprint(admin_bp)

        from .user import user_bp, user             # noqa: F401
        app.register_blueprint(user_bp)

        from .home import home_bp, home, logout     # noqa: F401
        app.register_blueprint(home_bp)  # , url_prefix='/home')

        from .auth import auth_bp, login, register  # noqa: F401
        app.register_blueprint(auth_bp)
        # from .admin import init_admin
        # init_admin(app)

        # Compile CSS
        from smrtuncrndsh.assets import compile_assets
        compile_assets(app)

        # Import Dash applications
        from smrtuncrndsh.dash_apps.dashboard import create_dashboard
        create_dashboard(app)

        from smrtuncrndsh.dash_apps.graph import create_graph
        create_graph(app)

        return app
