"""Initialize Flask app."""
import os
from flask import Flask
from flask_migrate import Migrate
# from extra.get_config import get_config


def get_base_dir():
    return os.path.abspath(os.path.abspath(os.path.dirname(__file__)))


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
        from .models import db
        migrate = Migrate(app, db)          # noqa: F841

        from .admin import admin_bp, users, activation, delete_user, edit_user  # noqa: F401
        app.register_blueprint(admin_bp)

        from .user import user_bp, user             # noqa: F401
        app.register_blueprint(user_bp)

        from .home import home_bp, home, logout     # noqa: F401
        app.register_blueprint(home_bp)  # , url_prefix='/home')

        from .auth import auth_bp, login, register  # noqa: F401
        app.register_blueprint(auth_bp)

        # Compile CSS
        from smrtuncrndsh.assets import compile_assets
        compile_assets(app)

        # Import Dash applications
        from smrtuncrndsh.dash_apps.dashboard import create_dashboard
        create_dashboard(app)

        from smrtuncrndsh.dash_apps.shopping import create_shopping_dashboard
        create_shopping_dashboard(app)

        from smrtuncrndsh.dash_apps.dashboard_overview import create_dashboard_overview
        create_dashboard_overview(app)

        return app


def get_css_vars():
    BASE_DIR = get_base_dir()
    vars = {}
    with open(os.path.join(BASE_DIR, 'static', 'css', 'variables.css'), 'r') as css_file:
        for line in css_file:
            line = line.strip()
            if line.startswith('--'):
                key, value = line[:-1].replace('--', '').split(': ')
                vars[key] = value
    return vars


CSS_VARIABLES = get_css_vars()
