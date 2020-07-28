import logging

from dashboard.app import app, server
# from .index import layout
from dashboard.misc.generate_shopping_data import generate_shopping_data

logger = logging.getLogger()

# app.layout = layout

if __name__ == "__main__":
    logger.debug(f"Environment: {server.config['ENV']}")

    if server.config['DEBUG']:
        logger.debug(f"Debug: {server.config['DEBUG']}")
        logger.debug(f"Secret key: {server.config['SECRET_KEY']}")
        logger.debug(f"DATABASE_URI: {server.config['SQLALCHEMY_DATABASE_URI']}")

        logger.debug("Generating development shopping lists.")
        generate_shopping_data()

    app.run_server(
        debug=True,
        port=5000,
        host='0.0.0.0',
        threaded=True
    )
