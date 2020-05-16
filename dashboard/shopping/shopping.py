#!/usr/bin/env python3

import logging

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
import shopping.add
import shopping.overview

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
        value="shopping-overview-tab",
        parent_className='custom__main__tabs',
        className='custom__main__tabs__container',
        children=[
            dcc.Tab(
                label="Overview",
                value="shopping-overview-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
            dcc.Tab(
                label="Add Shopping List",
                value="shopping-add-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
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
    logger.debug(f"'render_shopping_tab' called with tab '{tab}'.'")
    if tab == 'shopping-overview-tab':
        layout = shopping.overview.layout
    elif tab == 'shopping-add-tab':
        layout = shopping.add.layout
    return layout
