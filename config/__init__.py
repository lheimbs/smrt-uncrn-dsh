import os
import sys
from .config import config_dict
from smrtuncrndsh import get_base_dir


def init_config(app):
    env = os.environ.get('FLASK_ENV', 'development')
    app.logger.debug(f"FLASK_ENV={env}")

    try:
        config = config_dict[env]
        app.logger.debug(f"FLASK_CONFIG: {str(config)[22:-2]}")
    except KeyError:
        app.logger.error('Error: Invalid FLASK_ENV environment variable entry.')
        sys.exit(1)
    app.config.from_object(config)
    app.logger.debug(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    BASE_DIR = get_base_dir()
    if not os.path.exists(os.path.join(BASE_DIR, app.config['UPLOAD_FOLDER'])):
        app.logger.debug(f"UPLOAD_FOLDER '{os.path.join(BASE_DIR, app.config['UPLOAD_FOLDER'])}' does not exist. Creating it!")
        os.mkdir(os.path.join(BASE_DIR, app.config['UPLOAD_FOLDER']))
