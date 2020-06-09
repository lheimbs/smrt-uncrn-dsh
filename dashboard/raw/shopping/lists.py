#!/usr/bin/env python3

import logging
from math import ceil
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
        dcc.Store('raw-shopping-lists-date-store'),
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
                html.P('Settings:', className='one column sidebar_settings_item'),
                daq.BooleanSwitch(
                    className='one column sidebar_settings_item',
                    id='raw-shopping-lists-settings-show-hide-switch',
                    on=True,
                    color=COLORS['foreground'],
                ),
                html.Button(
                    '\U00002190 Previous',
                    id='raw-shopping-lists-previous',
                    className='offset-by-one two columns',
                    n_clicks=0,
                ),
                html.Div(
                    id='raw-shopping-list-page-container',
                    className='offset-by-two two columns',
                    children=[html.P("")]
                ),
                html.Button(
                    'Next \u2192',
                    id='raw-shopping-lists-next',
                    className='offset-by-two two columns',
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
                            value=5,
                            min=1,
                            max=10,
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
                            n_clicks=0,
                        ),
                    ]
                ),
            ],
        ),
        html.Div(
            id='raw-shopping-lists-content',
            className="one_row sidebar_content",
            children=[
                dcc.Loading(
                    id="raw-shopping-lists-data-loading",
                    type="default", color=COLORS['foreground'],
                ),
            ],
        )
    ],
)


def add_or_remove_older_lists(data, start, prev_start, prev_start_actual):
    start_actual = prev_start_actual
    if start > prev_start_actual:
        lists = []
        for i, shopping_list in enumerate(data):
            date = datetime.fromisoformat(shopping_list['date'])
            if not i:
                start_actual = date
            if date >= start:
                lists.append(shopping_list)
                if date < start_actual:
                    start_actual = date
        data = lists
    elif start < prev_start:
        lists = sql.get_shopping_lists(start, prev_start)
        start_actual = min([datetime.fromisoformat(slist['date']) for slist in lists])
        data = lists + data
    return data, start_actual


def add_or_remove_newer_lists(data, end, prev_end, prev_end_actual):
    end_actual = prev_end_actual
    if end > prev_end:
        lists = sql.get_shopping_lists(prev_end, end)
        end_actual = max([datetime.fromisoformat(slist['date']) for slist in lists])
        data += lists
    elif end < prev_end_actual:
        lists = []
        for i, shopping_list in enumerate(data):
            date = datetime.fromisoformat(shopping_list['date'])
            if not i:
                end_actual = date
            if datetime.fromisoformat(shopping_list['date']) <= end:
                lists.append(shopping_list)
                if date > end_actual:
                    end_actual = date
        data = lists
    return data, end_actual


@app.callback(
    Output('raw-shopping-list-page-container', 'children'),
    [Input('raw-shopping-lists-page-store', 'data')]
)
def update_lists_pages(page):
    if not page:
        raise PreventUpdate
    else:
        return (
            html.P(f"{page['current'] + 1}"),
            html.P("/"),
            html.P(f"{page['max']}")
        )


@app.callback(
    [
        Output('raw-shopping-lists-lists-store', 'data'),
        Output('raw-shopping-lists-date-store', 'data'),
    ],
    [
        Input('raw-shopping-lists-settings-date-picker', 'start_date'),
        Input('raw-shopping-lists-settings-date-picker', 'end_date'),
    ],
    [
        State('raw-shopping-lists-lists-store', 'data'),
        State('raw-shopping-lists-date-store', 'data'),
        State('error-store', 'data'),
    ]
)
def get_shopping_lists(start, end, data, prev_dates, errors):
    if errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return None, None
    elif not start or not end:
        logger.warning("Start / Enddate is missing.")
        return None, None

    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')

    if not data:
        # Get lists based on start-/end-date
        data = sql.get_shopping_lists(start, end)
        dates = [datetime.fromisoformat(shopping_list['date']) for shopping_list in data]
        dates.sort()
        prev_dates = {'start': start, 'start_actual': dates[0], 'end': end, 'end_actual': dates[-1]}
    else:
        # adapt list
        prev_start = datetime.fromisoformat(prev_dates['start'])
        prev_end = datetime.fromisoformat(prev_dates['end'])
        prev_start_actual = datetime.fromisoformat(prev_dates['start_actual'])
        prev_end_actual = datetime.fromisoformat(prev_dates['end_actual'])

        data, prev_dates['start_actual'] = add_or_remove_older_lists(data, start, prev_start, prev_start_actual)
        data, prev_dates['end_actual'] = add_or_remove_newer_lists(data, end, prev_end, prev_end_actual)

        prev_dates['end'] = end
        prev_dates['start'] = start
    return data, prev_dates


@app.callback(
    Output('raw-shopping-lists-data-loading', 'children'),
    [
        Input('raw-shopping-lists-lists-store', 'data'),
        Input('raw-shopping-lists-page-store', 'data'),
    ],
    [
        State('error-store', 'data'),
    ]
)
def load_shopping_lists(data, page, errors):
    if errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return html.P(
            "Database Error! Please try again later.",
            style={'color': COLORS['error'], 'textAlign': 'center'}
        )
    elif not data:
        children = [html.P("No lists in this timeframe avaliable.", style={'color': COLORS['warning']})]
    else:
        lists = data[page['current'] * page['n_listperpage']:(page['current'] + 1) * page['n_listperpage']]
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
                            html.P(
                                datetime.fromisoformat(shopping_list['date']).strftime('%a, %d. %b %Y'),
                                className='date item',
                            ),
                            html.P(shopping_list['price'], className='price item'),
                            html.P(
                                shopping_list['shop']['name'] if shopping_list['shop'] else 'None',
                                className='shop item',
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


@app.callback(
    Output('raw-shopping-lists-page-store', 'data'),
    [
        Input('raw-shopping-lists-reload', 'n_clicks'),
        Input('raw-shopping-lists-previous', 'n_clicks'),
        Input('raw-shopping-lists-next', 'n_clicks'),
        Input('raw-shopping-lists-settings-num-results', 'value'),
        Input('raw-shopping-lists-lists-store', 'data'),
    ],
    [
        State('raw-shopping-lists-page-store', 'data'),
    ]
)
def update_page_store(n_reload, previous, n_next, lists_per_page, data, page):
    if not data:
        raise PreventUpdate
    elif not page:
        return {
            'current': 0,
            'max': ceil(len(data) / lists_per_page),
            'n_reload': n_reload,
            'n_previous': previous,
            'n_next': n_next,
            'n_listperpage': lists_per_page,
        }

    if n_reload > page['n_reload']:
        page['n_reload'] = n_reload
        page['current'] = 0
    if previous > page['n_previous']:
        page['n_previous'] = previous
        if page['current'] - 1 >= 0:
            page['current'] -= 1
    if n_next > page['n_next']:
        page['n_next'] = n_next
        if page['current'] + 1 < page['max']:
            page['current'] += 1
    if lists_per_page != page['n_listperpage']:
        page['n_listperpage'] = lists_per_page
        page['max'] = ceil(len(data) / lists_per_page)
    return page


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
