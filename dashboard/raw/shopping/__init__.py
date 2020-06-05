#!/usr/bin/env python3

import logging

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from dashboard.app import app
from . import lists
from . import items
from . import shops

logger = logging.getLogger()

layout = html.Div([
    dcc.Tabs(
        id="raw-shopping-main-tabs",
        persistence=True,
        parent_className='custom__main__tabs',
        className='custom__main__tabs__container',
        children=[
            dcc.Tab(
                label="Shopping Lists",
                value="raw-shopping-lists-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
            dcc.Tab(
                label="Items",
                value="raw-shopping-items-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
            dcc.Tab(
                label="Shops",
                value="raw-shopping-shops-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
        ]
    ),
    html.Div(
        id="raw-shopping-tabs-content",
        className="app__tab__content"
    ),
])


@app.callback(Output('raw-shopping-tabs-content', 'children'),
              [Input('raw-shopping-main-tabs', 'value')])
def render_raw_shopping_content(tab):
    if tab == 'raw-shopping-lists-tab':
        layout = lists.layout
    elif tab == 'raw-shopping-items-tab':
        layout = items.layout
    elif tab == 'raw-shopping-shops-tab':
        layout = shops.layout
    else:
        layout = items.layout
    return layout
