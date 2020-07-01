import os

import dash_html_components as html
from dash import Dash
from flask import current_app

from .layout import dash_template, dash_template_from_jinja


def create_dashboard(server):
    """Create a Plotly Dash dashboard."""
    assets_path = os.path.join(os.getcwd(), 'flask_dash', 'static')
    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/dashboard/',
        # external_stylesheets=[
        #     '/static/dist/css/styles.css',
        # ],
        assets_folder=assets_path,
    )
    if (dash_app.logger.hasHandlers()):
        dash_app.logger.handlers.clear()

    # Custom HTML layout
    dash_app.index_string = dash_template_from_jinja() # dash_template()

    # Create Dash Layout
    dash_app.layout = html.P('lol', id='dash-container')
    return dash_app.server
