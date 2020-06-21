#!/usr/bin/env python3

import logging

import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State
# from dash.exceptions import PreventUpdate

from dashboard.app import app, COLORS
from .. import sql

logger = logging.getLogger()

layout = html.Div(
    className="row one_row",
    children=[
        dcc.Store(id='raw-shopping-shops-previous-store'),
        dbc.Alert(
            id='raw-shopping-save-shops-alert',
            className='notification_alert',
            duration=10000 * 5,
            dismissable=True,
            fade=True,
            is_open=False,
        ),
        html.Div(
            className='settings_open_close row',
            style={'marginTop': '5px'},
            children=[
                html.P('Settings:', className='one column sidebar_settings_item'),
                daq.BooleanSwitch(
                    className='one column sidebar_settings_item',
                    id='raw-shopping-shops-settings-show-hide-switch',
                    on=True,
                    color=COLORS['foreground'],
                ),
                # html.Button(
                #     'Edit',
                #     id='raw-shopping-shops-edit',
                #     className='offset-by-one two columns',
                #     n_clicks=0,
                # ),
                # html.Button(
                #     'Save',
                #     id='raw-shopping-shops-save',
                #     className='offset-by-five two columns',
                #     n_clicks=0,
                # ),
            ],
        ),
        html.Div(
            id='raw-shopping-shops-settings-sidebar',
            className="sidebar",
            children=[
                html.Div(
                    className='card',
                    children=[
                        html.H6("Select number of entries:"),
                        dcc.Input(
                            id='raw-shopping-shops-settings-num-results',
                            type='number',
                            value=1000,
                            min=1,
                            max=99999,
                            debounce=True,
                        )
                    ]
                ),
                html.Div(
                    className='card',
                    style={'paddingBottom': '10px'},
                    children=[
                        html.H6("Search Shops:"),
                        dcc.Input(
                            id="raw-shopping-shops-settings-search",
                            type='text',
                            debounce=True,
                        )
                    ],
                ),
            ],
        ),
        html.Div(
            id='raw-shopping-shops-content',
            className="one_row sidebar_content",
            children=[
                dcc.Loading(
                    id="raw-shopping-shops-data-loading",
                    type="default",
                    color=COLORS['foreground'],
                    children=[
                        dash_table.DataTable(
                            id='raw-shopping-shops-data',
                            hidden_columns=['id'],
                            page_action="native",
                            page_current=0,
                            page_size=50,
                            # fixed_rows={'headers': True},
                            style_table={'height': '75vh', 'overflowY': 'auto'},
                            style_as_list_view=True,
                            style_header={
                                'backgroundColor': COLORS['background-medium'],
                                'fontWeight': 'bold'
                            },
                            style_cell={
                                'padding': '5px',
                                'textAlign': 'center',
                                'backgroundColor': COLORS['background'],
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': COLORS['background-sub-medium'],
                                }
                            ],
                        ),
                    ]
                ),
            ],
        ),
    ],
)


@app.callback(
    [
        Output('raw-shopping-shops-settings-sidebar', 'style'),
        Output('raw-shopping-shops-content', 'style'),
    ],
    [
        Input('raw-shopping-shops-settings-show-hide-switch', 'on'),
    ],
)
def toggle_raw_room_data_sidebar(toggle_button):
    if not toggle_button:
        return {'width': '0'}, {'marginLeft': '0'}
    return {'width': '15vw'}, {'marginLeft': '15vw'}


# @app.callback(
#     Output('raw-shopping-shops-data', 'editable'),
#     [Input('raw-shopping-shops-edit', 'n_clicks')]
# )
# def toggle_table_editable(n):
#     return bool(n % 2)


# @app.callback(
#     [
#         Output('raw-shopping-save-shops-alert', 'children'),
#         Output('raw-shopping-save-shops-alert', 'className'),
#         Output('raw-shopping-save-shops-alert', 'is_open'),
#         Output('raw-shopping-shops-settings-search', 'value')
#     ],
#     [Input('raw-shopping-shops-save', 'n_clicks')],
#     [
#         State('raw-shopping-shops-data', 'data'),
#         State('raw-shopping-shops-previous-store', 'data'),
#         State('raw-shopping-shops-settings-search', 'value'),
#         State('error-store', 'data'),
#     ]
# )
# def save_edited_shops(n, data, previous, search, errors):
#     logger.debug("Save edited shops from raw data to database.")
#     if not n or not previous:
#         raise PreventUpdate
#     elif errors['list'] or errors['category'] or errors['shop'] or errors['item']:
#         logger.warning("Neccessary Shopping tables do not exist in database!")
#         return (
#             [html.H4('Error'), html.Hr(), html.P("Database error. Please try again later.")],
#             'shopping_status_alert_failure',
#             True,
#             search,
#         )
#     else:
#         errors = []
#         for new, old in zip(data, previous):
#             if new != old:
#                 error = sql.update_shop(new)
#                 if error:
#                     errors.append(error)
#         if errors:
#             return (
#                 [html.H4('Errors occured updating shops')] + [html.P(error) for error in errors],
#                 'shopping_status_alert_failure',
#                 True,
#                 search
#             )
#         return 'Updated Shops', 'shopping_status_alert_success', True, search


@app.callback(
    [
        Output('raw-shopping-shops-data', 'columns'),
        Output('raw-shopping-shops-data', 'data'),
        Output('raw-shopping-shops-previous-store', 'data'),
    ],
    [
        Input('raw-shopping-shops-settings-num-results', 'value'),
        Input('raw-shopping-shops-settings-search', 'value'),
    ],
    [State('error-store', 'data')]
)
def get_raw_shopping_shops(limit, search, errors):
    if errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return (
            [{'name': 'Info', 'id': 'info'}],
            [{'info': 'Neccessary Shopping tables do not exist in database!'}],
            []
        )

    data = sql.get_raw_shopping_shops(limit, search)
    columns = [{
        'name': ' '.join(col.capitalize().split('_')),
        'id': col,
        'hideable': False,
    } for col in data.columns]

    return columns, data.to_dict('records'), data.to_dict('records')
