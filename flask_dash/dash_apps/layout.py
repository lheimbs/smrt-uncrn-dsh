"""Plotly Dash HTML layout override."""
import os
import uuid
import html

from flask import render_template

import dash_html_components as html
from flask_login import current_user


def apply_layout(app, layout):
    def serve_layout():
        if current_user and current_user.is_authenticated:
            session_id = str(uuid.uuid4())
            return html.Div([
                html.Div(session_id, id='session_id', style={'display': 'none'}),
                layout
            ])
        return html.Div('403 Access Denied')
    app.config.suppress_callback_exceptions = True
    app.layout = serve_layout


def dash_template_from_jinja():
    template = render_template('dash.html')
    idx = template.index('<div class="container">') + len('<div class="container">')
    template = template[:idx] + r'{%app_entry%}{%config%}{%scripts%}{%renderer%}' + template[idx:]
    print(template)

    return template


def dash_template():
    html_layout = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <meta charset="utf-8" />
            <meta http-equiv="X-UA-Compatible" content="IE=edge" />
            <meta name="HandheldFriendly" content="True" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
            <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
        </head>

        <body style="margin: 0">
    '''
    # <link rel="stylesheet" href="{{ url_for('static', filename='dist/css/styles.css') }}" />

    with open(
        os.path.join(os.getcwd(), 'flask_dash', 'templates', 'sidebar.html'),
        'r'
    ) as sidebar:
        for line in sidebar.readlines():
            html_layout += line

    html_layout += '<div id="main" class="main">'

    with open(
        os.path.join(os.getcwd(), 'flask_dash', 'templates', 'infobar.html'),
        'r'
    ) as infobar:
        for line in infobar.readlines():
            html_layout += line

    html_layout += '''
                <div class="container">
                
                    {%app_entry%}
                </div>
            </div>
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
    return html_layout
