from dash import Dash

from .layout import layout
from .callbacks import init_callbacks
from ..layout import apply_layout


def create_shopping_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/shopping/dashboard/',
    )
    if (dash_app.logger.hasHandlers()):
        dash_app.logger.handlers.clear()

    apply_layout(
        dash_app, layout,
        activated_only=True,
        template_str="shopping-dashboard-page",
        title="Shopping Dashboard"
    )
    init_callbacks(dash_app)
    return dash_app.server
