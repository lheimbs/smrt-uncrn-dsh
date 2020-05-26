
from .app import app
from .index import layout

app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True, port=5002, host='0.0.0.0', threaded=True)
    # Deleted 'self.logger.setLevel' from dash.py so debug messages are getting logged in callbacks
    # logging.getLogger('werkzeug').setLevel(logging.ERROR)
    # app.logger.setLevel(logging.Debug)