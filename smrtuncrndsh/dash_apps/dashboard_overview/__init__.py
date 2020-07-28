from ..layout import CustomDash
from .layout import layout
from .callbacks import init_callbacks


def make_dash_app():
    dash_app = CustomDash(
        name=__name__,
        assets_folder='static',
        server=False,
        routes_pathname_prefix='/dashboard/overview/',
        template="dashboard-overview-page",
        title="Dashboard"
    )
    dash_app.layout = layout
    init_callbacks(dash_app)
    return dash_app
