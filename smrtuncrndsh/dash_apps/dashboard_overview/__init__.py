from ..layout import DashFlaskyfied
from .layout import layout
from .callbacks import init_callbacks


def make_dash_app():
    dash_app = DashFlaskyfied(
        server=False,
        routes_pathname_prefix='/dashboard/overview/',
        template_str="dashboard-overview-page",
        title="Dashboard",
    )
    dash_app.layout = layout
    init_callbacks(dash_app)
    return dash_app
