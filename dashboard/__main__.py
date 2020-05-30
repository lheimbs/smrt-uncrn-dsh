
import logging

from .app import app, server
from .index import layout, generate_shopping_data

logger = logging.getLogger()

app.layout = layout

if __name__ == "__main__":
    logger.debug(f"Environment: {server.config['ENV']}")
    logger.debug(f"Debug: {server.config['DEBUG']}")
    logger.debug(f"Secret key: {server.config['SECRET_KEY']}")

    logger.debug(f"DATABASE_URI: {server.config['SQLALCHEMY_DATABASE_URI']}")

    if server.config['DEBUG']:
        logger.debug("Generating development shopping lists.")
        generate_shopping_data()

    app.run_server(
        debug=True,
        port=5000,
        host='0.0.0.0',
        threaded=True
    )
    # Deleted 'self.logger.setLevel' from dash.py so debug messages are getting logged in callbacks
    # logging.getLogger('werkzeug').setLevel(logging.ERROR)
    # app.logger.setLevel(logging.Debug)
