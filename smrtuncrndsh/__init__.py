"""Initialize Flask app."""
import os
from flask import Flask
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman

csrf = CSRFProtect()
talisman = Talisman()


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

    from .shopping_add import shopping_add_bp, add, query_shops  # noqa: F401
    app.register_blueprint(shopping_add_bp)


def register_dash(app):
    # Import and register Dash applications
    from smrtuncrndsh.dash_apps.layout import register_dash_app

    from smrtuncrndsh.dash_apps.dashboard import make_dash_app as dashboard
    register_dash_app(app, dashboard(), 'activation_required')

    from smrtuncrndsh.dash_apps.dashboard_overview import make_dash_app as dashboard_overview
    register_dash_app(app, dashboard_overview(), 'activation_required')

    from smrtuncrndsh.dash_apps.shopping import make_dash_app as shopping
    register_dash_app(app, shopping(), 'activation_required')


def create_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)

    from config import init_config
    init_config(app)

    csrf.init_app(app)

    # Compile CSS
    from smrtuncrndsh.assets import compile_assets
    compile_assets(app)

    from .models import init_db
    init_db(app)

    from .auth import init_login
    init_login(app)

    from .errors import register_handlers
    register_handlers(app)

    with app.app_context(), app.test_request_context():
        from .models import db
        migrate = Migrate(app, db)          # noqa: F841

        talisman.init_app(
            app,
            content_security_policy=app.config['CSP'],
            content_security_policy_nonce_in=['script-src'],
        )
        register_blueprints(app)
        register_dash(app)

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
