#!/usr/bin/env python3

import logging

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from ..app import app
from . import add
from . import overview

logger = logging.getLogger()

layout = html.Div([
    dcc.Store(
        id='shopping-products-store',
        storage_type='session',
    ),
    dcc.Store(
        id='shopping-shops-store',
        storage_type='session',
    ),
    dcc.Tabs(
        id="shopping-main-tabs",
        persistence=True,
        # value="shopping-overview-tab",
        parent_className='custom__main__tabs',
        className='custom__main__tabs__container',
        children=[
            dcc.Tab(
                label="Overview",
                value="shopping-overview-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
            # dcc.Tab(
            #     label="Add Shopping List",
            #     value="shopping-add-tab",
            #     className='custom__main__sub__tab',
            #     selected_className='custom__main__sub__tab____selected',
            # ),
        ]
    ),
    html.Div(
        id="shopping-tabs-content",
        className="app__tab__content"
    ),
])


@app.callback(Output('shopping-tabs-content', 'children'),
              [Input('shopping-main-tabs', 'value')])
def render_shopping_content(tab):
    if tab == 'shopping-add-tab':
        layout = add.layout
    elif tab == 'shopping-overview-tab':
        layout = overview.layout
    else:
        layout = overview.layout
    return layout
