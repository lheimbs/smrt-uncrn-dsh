"""Plotly Dash HTML layout override."""

from dash import Dash
from flask import render_template, current_app
from flask_login import login_required

from smrtuncrndsh.auth import activation_required


def register_dash_app(app, dash_app, *args):
    dash_app.init_app(app)

    if app.config['DEBUG']:
        dash_app.enable_dev_tools(debug=True)
    if dash_app.logger.hasHandlers():
        dash_app.logger.handlers.clear()

    if 'activation_required' in args:
        for view_name, view_method in dash_app.server.view_functions.items():
            if view_name.startswith(dash_app.config['routes_pathname_prefix']):
                dash_app.server.view_functions[view_name] = activation_required(view_method)
    elif 'login_required' in args:
        for view_name, view_method in dash_app.server.view_functions.items():
            if view_name.startswith(dash_app.config['routes_pathname_prefix']):
                dash_app.server.view_functions[view_name] = login_required(view_method)


class DashFlaskyfied(Dash):
    def __init__(self, template_str='', title='', *args, **kwargs):
        Dash.__init__(self, *args, **kwargs)
        self.template_str = template_str
        self.title = title

    def interpolate_index(self, **kwargs):
        current_app.logger.debug("serve index")
        template = render_template('base.html', template=self.template_str, title=self.title)
        idx = template.index('<main>') + len('<main>')
        template = template[:idx] + f'{kwargs["app_entry"]}' + template[idx:]
        idx = template.index('</body>')
        template = template[:idx] + (
            f'<dash_footer>{kwargs["config"]}{kwargs["scripts"]}{kwargs["renderer"]}</dash_footer>'
        ) + template[idx:]
        return template
