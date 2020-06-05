#!/usr/bin/env python3

import logging

import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dashboard.app import app, COLORS
from .. import sql

logger = logging.getLogger()

layout = html.Div(
    className="row one_row",
    children=[
        dcc.Store('raw-shopping-items-previous-store'),
        dbc.Alert(
            id='raw-shopping-save-items-alert',
            duration=10000 * 5,
            dismissable=True,
            fade=True,
            is_open=False,
        ),
        html.Div(
            className='settings_open_close row',
            style={'marginTop': '5px'},
            children=[
                html.P('Settings:', className='one column', style={'marginTop': '5px', 'marginBottom': '0px'}),
                daq.BooleanSwitch(
                    className='one column',
                    id='raw-shopping-items-settings-show-hide-switch',
                    on=True,
                    color=COLORS['foreground'],
                ),
                html.Button(
                    'Edit',
                    id='raw-shopping-items-edit',
                    className='offset-by-one two columns',
                    n_clicks=0,
                ),
                html.Button(
                    'Save',
                    id='raw-shopping-items-save',
                    className='offset-by-five two columns',
                    n_clicks=0,
                ),
            ],
        ),
        html.Div(
            id='raw-shopping-items-settings-sidebar',
            className="sidebar",
            children=[
                html.Div(
                    className='card',
                    children=[
                        html.H6("Select number of entries:"),
                        dcc.Input(
                            id='raw-shopping-items-settings-num-results',
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
                        html.H6("Search Items:"),
                        dcc.Input(
                            id="raw-shopping-items-settings-search",
                            type='text',
                            debounce=True,
                        )
                    ],
                ),
            ],
        ),
        html.Div(
            id='raw-shopping-items-content',
            className="one_row",
            children=[
                dcc.Loading(
                    id="raw-shopping-items-data-loading",
                    type="default", color=COLORS['foreground'],
                    children=[
                        dash_table.DataTable(
                            id='raw-shopping-items-data',
                            hidden_columns=['id'],
                            data=[],
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
        )
    ],
)


@app.callback(
    [
        Output('raw-shopping-items-settings-sidebar', 'style'),
        Output('raw-shopping-items-content', 'style'),
    ],
    [
        Input('raw-shopping-items-settings-show-hide-switch', 'on'),
    ],
)
def toggle_raw_room_data_sidebar(toggle_button):
    if not toggle_button:
        return {'width': '0'}, {'marginLeft': '0'}
    return {'width': '15vw'}, {'marginLeft': '15vw'}


@app.callback(
    Output('raw-shopping-items-data', 'editable'),
    [Input('raw-shopping-items-edit', 'n_clicks')]
)
def toggle_table_editable(n):
    return bool(n % 2)


@app.callback(
    [
        Output('raw-shopping-save-items-alert', 'children'),
        Output('raw-shopping-save-items-alert', 'className'),
        Output('raw-shopping-save-items-alert', 'is_open'),
        Output('raw-shopping-items-settings-search', 'value'),
    ],
    [Input('raw-shopping-items-save', 'n_clicks')],
    [
        State('raw-shopping-items-data', 'data'),
        State('raw-shopping-items-previous-store', 'data'),
        State('raw-shopping-items-settings-search', 'value'),
        State('error-store', 'data'),
    ]
)
def save_edited_items(n, data, previous, search, errors):
    if not n or previous == data:
        # return '', '', False
        raise PreventUpdate
    elif errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return (
            [html.H4('Error'), html.Hr(), html.P("Database error. Please try again later.")],
            'shopping_status_alert_failure',
            True,
            search,
        )
    else:
        status = True
        infos = []
        for new, old in zip(data, previous):
            if new != old:
                if type(new['sale']) == str:
                    new['sale'] = True if new['sale'].lower() == 'true' else False
                success, info = sql.update_items(new)
                status &= success
                infos += info
        if not status:
            return (
                [html.H4('Errors occured updating items')] + [html.P(info) for info in infos],
                'shopping_status_alert_failure',
                True,
                search,
            )
        return (
            [html.H4('Successfully updated items...')] + [html.P(info) for info in infos],
            'shopping_status_alert_success',
            True,
            search
        )


@app.callback(
    [
        Output('raw-shopping-items-data', 'columns'),
        Output('raw-shopping-items-data', 'data'),
        Output('raw-shopping-items-previous-store', 'data'),
    ],
    [
        Input('raw-shopping-items-settings-num-results', 'value'),
        Input('raw-shopping-items-settings-search', 'value'),
    ],
    [State('error-store', 'data')]
)
def get_raw_shopping_items(limit, search, errors):
    if errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return (
            [{'name': 'Info', 'id': 'info'}],
            [{'info': 'Neccessary Shopping tables do not exist in database!'}],
            []
        )

    data = sql.get_raw_shopping_items(limit, search)
    columns = [{
        'name': ' '.join(col.capitalize().split('_')),
        'id': col,
        'hideable': False,
    } for col in data.columns]
    return columns, data.to_dict('records'), data.to_dict('records')
