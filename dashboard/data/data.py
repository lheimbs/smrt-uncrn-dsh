#!/usr/bin/env python3

import logging

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
import data.overview
import data.graph

logger = logging.getLogger()

layout = html.Div([
    dcc.Tabs(
        id="data-main-tabs",
        value="data-overview-tab",
        parent_className='custom__main__tabs',
        className='custom__main__tabs__container',
        children=[
            dcc.Tab(
                label="Overview",
                value="data-overview-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
            dcc.Tab(
                label="Graph",
                value="data-graph-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
            # dcc.Tab(
            #     label="Settings",
            #     value="data-settings-tab",
            #     className='custom__main__sub__tab',
            #     selected_className='custom__main__sub__tab____selected',
            # ),
        ]
    ),
    html.Div(
        id="data-tabs-content",
        className="app__tab__content"
    ),
])


@app.callback(Output('data-tabs-content', 'children'),
              [Input('data-main-tabs', 'value')])
def render_data_content(tab):
    if tab == 'data-overview-tab':
        layout = data.overview.layout
    elif tab == 'data-graph-tab':
        layout = data.graph.layout
    elif tab == 'data-settings-tab':
        layout = html.Div("Settings")
    return layout
