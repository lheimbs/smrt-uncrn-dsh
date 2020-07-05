import os

import dash_html_components as html
from dash import Dash

from ..layout import apply_layout


def create_dashboard(server):
    """Create a Plotly Dash dashboard."""
    assets_path = os.path.join(os.getcwd(), 'smrtuncrndsh', 'static')
    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/dashboard/',
        assets_folder=assets_path,
    )
    if (dash_app.logger.hasHandlers()):
        dash_app.logger.handlers.clear()

    apply_layout(dash_app, html.Div("lol"), "dashboard-page")
    return dash_app.server
