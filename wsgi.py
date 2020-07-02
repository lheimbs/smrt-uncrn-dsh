"""Application entry point."""
import os
from logging.config import dictConfig

from smrtuncrndsh import create_app

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(module)15s - %(levelname)-8s : %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': os.environ.get('LOG_LEVEL', 'WARNING'),
        'handlers': ['wsgi']
    }
})


app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
