"""Plotly Dash HTML layout override."""

from dash import Dash
from flask import render_template, current_app

from flask_login import login_required

from smrtuncrndsh import csrf
from smrtuncrndsh.auth import activation_required


def register_dash_app(app, dash_app, *args):
    dash_app.init_app(app)

    if app.config['DEBUG']:
        dash_app.enable_dev_tools(debug=True)
    if dash_app.logger.hasHandlers():
        dash_app.logger.handlers.clear()

    for view_name, view_method in dash_app.server.view_functions.items():
        if view_name.startswith(dash_app.config['routes_pathname_prefix']):
            csrf.exempt(view_method)

            if current_app.config['DEBUG']:
                app.logger.warning("Debugging enabled. Skipping activation and login requirements for dash apps!")
            else:
                if 'activation_required' in args:
                    app.logger.debug(f"Enabling 'activation required' for view '{view_name}'.")
                    dash_app.server.view_functions[view_name] = activation_required(view_method)
                elif 'login_required' in args:
                    app.logger.debug(f"Enabling 'login required' for view '{view_name}'.")
                    dash_app.server.view_functions[view_name] = login_required(view_method)


class CustomDash(Dash):
    def __init__(self, template='', title='', *args, **kwargs):
        Dash.__init__(self, *args, **kwargs)
        self.template_str = template
        self.title = title

    def interpolate_index(self, **kwargs):
        current_app.logger.debug("serve index")
        template = render_template('dash_base.html', template=self.template_str, title=self.title)
        template = template.format(
            css=kwargs['css'],
            app_entry=kwargs['app_entry'],
            config=kwargs['config'],
            scripts=kwargs['scripts'],
            renderer=kwargs['renderer']
        )
        return template
