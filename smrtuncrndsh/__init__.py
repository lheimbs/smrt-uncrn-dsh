"""Initialize Flask app."""
import os
from flask import Flask
from flask_migrate import Migrate
# from extra.get_config import get_config


def get_base_dir():
    return os.path.abspath(os.path.abspath(os.path.dirname(__file__)))


def register_blueprints(app):
    from .admin import admin_bp                                             # noqa: F401
    from .admin.users import users, edit_user, delete_user, activation, new_user      # noqa: F401
    from .admin.shopping.lists import shopping_list  # noqa: F401
    from .admin.shopping.items import shopping_item  # noqa: F401
    from .admin.shopping.shops import shopping_shop  # noqa: F401
    from .admin.shopping.categories import shopping_category  # noqa: F401
    from .admin.room_data import room_data  # noqa: F401
    from .admin.rf_data import rf_data  # noqa: F401
    from .admin.mqtt import mqtt  # noqa: F401
    from .admin.probe_request import probe_request  # noqa: F401
    from .admin.state import state  # noqa: F401
    from .admin.tablet_battery import tablet_battery  # noqa: F401
    app.register_blueprint(admin_bp)

    from .user import user_bp, user             # noqa: F401
    app.register_blueprint(user_bp)

    from .home import home_bp, home, logout     # noqa: F401
    app.register_blueprint(home_bp)  # , url_prefix='/home')

    from .auth import auth_bp, login, register  # noqa: F401
    app.register_blueprint(auth_bp)


def register_dash(app):
    # Import Dash applications
    from smrtuncrndsh.dash_apps.dashboard import create_dashboard
    create_dashboard(app)

    from smrtuncrndsh.dash_apps.shopping import create_shopping_dashboard
    create_shopping_dashboard(app)

    from smrtuncrndsh.dash_apps.dashboard_overview import create_dashboard_overview
    create_dashboard_overview(app)


def create_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)

    from config import init_config
    init_config(app)

    from .models import init_db
    init_db(app)

    from .auth import init_login
    init_login(app)

    from .errors import register_handlers
    register_handlers(app)

    with app.app_context(), app.test_request_context():
        from .models import db
        migrate = Migrate(app, db)          # noqa: F841

        register_blueprints(app)
        register_dash(app)

        # Compile CSS
        from smrtuncrndsh.assets import compile_assets
        compile_assets(app)

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
