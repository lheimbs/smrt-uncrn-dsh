#!/usr/bin/env python3

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
        dcc.Store('raw-shopping-lists-page-store', data=0),
        dcc.Store('raw-shopping-lists-lists-store'),
        dbc.Alert(
            id='raw-shopping-save-lists-alert',
            duration=10000 * 5,
            dismissable=True,
            fade=True,
            is_open=False,
        ),
        html.Div(
            className='settings_open_close row',
            style={'marginTop': '5px', 'marginBottom': '10px'},
            children=[
                html.P('Settings:', className='one column', style={'marginTop': '5px', 'marginBottom': '0px'}),
                daq.BooleanSwitch(
                    className='one column',
                    id='raw-shopping-lists-settings-show-hide-switch',
                    on=True,
                    color=COLORS['foreground'],
                ),
                html.Button(
                    'Edit',
                    id='raw-shopping-lists-edit',
                    className='offset-by-one two columns',
                    n_clicks=0,
                ),
                html.Button(
                    'Save',
                    id='raw-shopping-lists-save',
                    className='offset-by-five two columns',
                    n_clicks=0,
                ),
            ],
        ),
        html.Div(
            id='raw-shopping-lists-settings-sidebar',
            className="sidebar",
            children=[
                html.Div(
                    className='card',
                    children=[
                        html.H6("Lists per page:"),
                        dcc.Input(
                            id='raw-shopping-lists-settings-num-results',
                            type='number',
                            value=10,
                            min=1,
                            max=100,
                            debounce=True,
                        )
                    ]
                ),
                html.Div(
                    className='card',
                    style={'paddingBottom': '10px'},
                    children=[
                        html.H6("Choose Daterange:"),
                        dcc.DatePickerRange(
                            id="raw-shopping-lists-settings-date-picker",
                            start_date_placeholder_text="Start Period",
                            end_date_placeholder_text="End Period",
                            # minimum_nights=1,
                            display_format='DD MM Y',
                            month_format='MM YYYY',
                            day_size=35,
                            first_day_of_week=1,
                            persistence=True,
                            persistence_type='session',
                            updatemode='bothdates',
                            with_full_screen_portal=True,
                            end_date=datetime.now().date() - relativedelta(days=1),
                            start_date=datetime.now().date() - relativedelta(weeks=4),
                        ),
                    ],
                ),
                html.Div(
                    className='card',
                    children=[
                        html.Button(
                            "Reload",
                            id='raw-shopping-lists-reload',
                        ),
                    ]
                ),
            ],
        ),
        html.Div(
            id='raw-shopping-lists-content',
            className="one_row",
            children=[
                dcc.Loading(
                    id="raw-shopping-lists-data-loading",
                    type="default", color=COLORS['foreground'],
                ),
            ],
        )
    ],
)


@app.callback(
    Output('raw-shopping-lists-lists-store', 'data'),
    [
        # Input('raw-shopping-lists-lists-store', 'loading_state'),
        Input('raw-shopping-lists-settings-date-picker', 'start_date'),
        Input('raw-shopping-lists-settings-date-picker', 'end_date'),
    ],
    [
        State('raw-shopping-lists-lists-store', 'data'),
        State('error-store', 'data'),
    ]
)
def get_shopping_lists(start, end, data, errors):
    if errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return None
    elif not start or not end:
        logger.warning("Start / Enddate is missing.")
        return None

    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')

    if not data:
        # Get lists based on start-/end-date
        lists = sql.get_shopping_lists(start, end)
    else:
        # Shrink or expand the current lists store
        dates = [datetime.fromisoformat(shopping_list['date']) for shopping_list in data]
        dates.sort()
        min_date, max_date = dates[0], dates[-1]

        lists = None

        if start < min_date:
            lists = sql.get_shopping_lists(start, min_date)
            lists += data
        if max_date < end:
            lists = sql.get_shopping_lists(max_date, end)
            lists = data + lists

    return lists


@app.callback(
    Output('raw-shopping-lists-data-loading', 'children'),
    [
        Input('raw-shopping-lists-reload', 'n_clicks'),
        Input('raw-shopping-lists-page-store', 'data'),
        Input('raw-shopping-lists-lists-store', 'data'),
    ],
    [
        State('raw-shopping-lists-settings-num-results', 'value'),
        State('error-store', 'data'),
    ]
)
def load_shopping_lists(clicks, page, data, lists_per_page, errors):
    if errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return html.P("Database Error! Please try again later.", style={'color': COLORS['error']})

    if not data:
        children = [html.P("No lists in this timeframe avaliable.", style={'color': COLORS['warning']})]
    else:
        lists = data[page * lists_per_page:(page + 1) * lists_per_page]
        if lists:
            children = []
            for shopping_list in lists:
                item_columns = [
                    {'name': 'name', 'id': 'name'},
                    {'name': 'price', 'id': 'price'},
                    {'name': 'volume', 'id': 'volume'},
                    {'name': 'price_per_volume', 'id': 'price_per_volume'},
                    {'name': 'sale', 'id': 'sale'},
                    {'name': 'note', 'id': 'note'},
                    {'name': 'category', 'id': 'category'},
                ]
                items = []
                for item in shopping_list['items']:
                    items.append({
                        'name': item['name'],
                        'price': item['price'],
                        'volume': item['volume'],
                        'price_per_volume': item['price_per_volume'],
                        'sale': item['sale'],
                        'note': item['note'],
                        'category': item['category']['name'] if item['category'] else ''
                    })

                children += [
                    html.Div(
                        className='list_container',
                        children=[
                            html.B([html.P('Date')], className='date_header grid_card item'),
                            html.B([html.P('Price')], className='price_header grid_card item'),
                            html.B([html.P('Shop')], className='shop_header grid_card item'),
                            html.B([html.P('Category')], className='category_header grid_card item'),
                            html.P(datetime.fromisoformat(shopping_list['date']).strftime('%c'), className='date item'),
                            html.P(shopping_list['price'], className='price item'),
                            html.P(
                                shopping_list['shop']['name'] if shopping_list['shop'] else 'None', className='shop item'
                            ),
                            html.P(
                                shopping_list[
                                    'category'
                                ]['name'] if shopping_list['category'] else 'None',
                                className='category item'
                            ),
                            html.Details(
                                [
                                    html.Summary('Items'),
                                    dash_table.DataTable(
                                        id='raw-shopping-lists-data',
                                        # hidden_columns=['id'],
                                        columns=item_columns,
                                        data=items,
                                        page_action="native",
                                        page_current=0,
                                        page_size=50,
                                        # fixed_rows={'headers': True},
                                        # style_table={'height': '75vh', 'overflowY': 'auto'},
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
                                    # html.Div(
                                    #     id='raw-shopping-lists-items',
                                    #     className='list_items_content',
                                    #     children=[
                                    #         html.Table([
                                    #             html.Thead([
                                    #                 html.Th('Item'),
                                    #                 html.Th('Price'),
                                    #                 html.Th('Volume'),
                                    #                 html.Th('Price per volume'),
                                    #                 html.Th('Sale'),
                                    #                 html.Th('Note'),
                                    #                 html.Th('Category'),
                                    #             ]),
                                    #             html.Tbody(children=items),
                                    #         ]),
                                    #     ]
                                    # )
                                ],
                                className='details item',
                            ),
                            html.Button(
                                'Edit',
                                className='edit item',
                                id={
                                    'type': 'raw-shopping-lists-show-items-button',
                                    'id': shopping_list['id'],
                                }
                            ),
                        ]
                    ),
                    html.Br(),
                ]
        else:
            raise PreventUpdate
    return children



'''
children=[
    
]
'''


@app.callback(
    [
        Output('raw-shopping-lists-settings-sidebar', 'style'),
        Output('raw-shopping-lists-content', 'style'),
    ],
    [
        Input('raw-shopping-lists-settings-show-hide-switch', 'on'),
    ],
)
def toggle_raw_room_data_sidebar(toggle_button):
    if not toggle_button:
        return {'width': '0'}, {'marginLeft': '0'}
    return {'width': '15vw'}, {'marginLeft': '16vw'}


'''
@app.callback(
    [
        Output('raw-shopping-save-lists-alert', 'children'),
        Output('raw-shopping-save-lists-alert', 'className'),
        Output('raw-shopping-save-lists-alert', 'is_open'),
        Output('raw-shopping-lists-settings-search', 'value'),
    ],
    [Input('raw-shopping-lists-save', 'n_clicks')],
    [
        State('raw-shopping-lists-data', 'data'),
        State('raw-shopping-lists-previous-store', 'data'),
        State('raw-shopping-lists-settings-search', 'value'),
        State('error-store', 'data'),
    ]
)
def save_edited_lists(n, data, previous, search, errors):
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
                success, info = sql.update_lists(new)
                status &= success
                infos += info
        if not status:
            return (
                [html.H4('Errors occured updating lists')] + [html.P(info) for info in infos],
                'shopping_status_alert_failure',
                True,
                search,
            )
        return (
            [html.H4('Successfully updated lists...')] + [html.P(info) for info in infos],
            'shopping_status_alert_success',
            True,
            search
        )
'''


'''
@app.callback(
    [
        Output('raw-shopping-lists-data', 'columns'),
        Output('raw-shopping-lists-data', 'data'),
        Output('raw-shopping-lists-previous-store', 'data'),
    ],
    [
        Input('raw-shopping-lists-settings-date-picker', 'start_date'),
        Input('raw-shopping-lists-settings-date-picker', 'end_date'),
    ],
    [State('error-store', 'data')]
)
def get_raw_shopping_lists(start, end, errors):
    if errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return (
            [{'name': 'Info', 'id': 'info'}],
            [{'info': 'Neccessary Shopping tables do not exist in database!'}],
            []
        )

    data = sql.get_raw_shopping_lists(limit, search)
    columns = [{
        'name': ' '.join(col.capitalize().split('_')),
        'id': col,
        'hideable': False,
    } for col in data.columns]
    return columns, data.to_dict('records'), data.to_dict('records')
'''
