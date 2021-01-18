import logging

from smrtuncrndsh import create_app

logger = logging.getLogger()

if __name__ == "__main__":
    app = create_app()
    logger.debug(f"Environment: {app.config['ENV']}")

    app.run(
        debug=True,
        port=5000,
        host='0.0.0.0',
        threaded=True
    )
