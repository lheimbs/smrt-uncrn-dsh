#!/usr/bin/env python3

import logging
from datetime import datetime

import numpy as np
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

from app import app

logger = logging.getLogger()

# constants
N_SHOPPING_ITEMS = 15

layout = html.Div(
    className='shopping__add__container',
    children=[
        dcc.Store(id='shopping-save-clear-clicks'),
        html.Br(),
        html.Div(
            className='row shopping__add__header',
            children=[
                html.Div(
                    className='one column',
                    children=[
                        html.H6("Date:", className='form__header')
                    ]
                ),
                html.Div(
                    className='two columns',
                    children=[
                        dcc.DatePickerSingle(
                            id="shopping-new-list-date",
                            placeholder="Date...",
                            display_format='DD MM Y',
                            month_format='MM YYYY',
                            day_size=35,
                            first_day_of_week=1,
                            persistence=True,
                            persistence_type='session',
                            with_full_screen_portal=True,
                        )
                    ]
                ),
                html.Div(
                    className='two columns',
                    children=[
                        html.H6("Sum total:", className='form__header')
                    ]
                ),
                html.Div(
                    className='two columns',
                    children=[
                        dcc.Input(
                            id='shopping-new-price',
                            type="number",
                            placeholder='Price...',
                            # pattern=r"\d{1,3}[,.]{0,1}\d{0,2}",  # ignored in number input
                        )
                    ]
                ),
                html.Div(
                    className='one columns',
                    children=[
                        html.H6("Shop:", className='form__header')
                    ]
                ),
                html.Div(
                    className='two columns',
                    children=[
                        html.Datalist(
                            id='shopping-shops-list',
                        ),
                        dcc.Input(
                            id='shopping-new-shop',
                            placeholder="Shop...",
                            list='shopping-shops-list',
                            # pattern=r"\d{1,3}[,.]{0,1}\d{0,2}",  # ignored in number input
                        )
                    ]
                ),
                html.Div(
                    className='one columns',
                    children=[
                        html.Button(
                            "Add another Item",
                            id='shopping-new-item-button',
                        )
                    ]
                ),
            ],
        ),
        html.Br(),
        html.Datalist(
            id='shopping-items-list',
        ),
        html.Div(
            id='shopping-add-items-list',
            className='shopping__add__items',
            children=[
                html.Div(
                    className='row add__items',
                    children=[
                        html.Div(
                            className='offset-by-two two columns',
                            children=[
                                dcc.Input(
                                    id={
                                        'type': 'shopping-new-item',
                                        'id': n,
                                    },
                                    placeholder="Item...",
                                    list='shopping-items-list',
                                )
                            ]
                        ),
                        html.Div(
                            className='two columns',
                            children=[
                                dcc.Input(
                                    id={
                                        'type': 'shopping-new-item-price',
                                        'id': n,
                                    },
                                    placeholder="Item Price...",
                                    type='number',
                                )
                            ]
                        ),
                        html.Div(
                            className='two columns',
                            children=[
                                dcc.Input(
                                    id={
                                        'type': 'shopping-new-item-note',
                                        'id': n,
                                    },
                                    placeholder="Note...",
                                )
                            ]
                        ),
                        html.Div(
                            className='offset-by-one column one column',
                            children=[
                                html.Button(
                                    "Remove Item",
                                    id={
                                        'type': 'shopping-remove-item',
                                        'id': n,
                                    },
                                )
                            ]
                        ),
                    ],
                )
                for n in range(0, N_SHOPPING_ITEMS)
            ]
        ),
        html.Br(),
        html.Div(
            className='row shopping__add__submit',
            children=[
                html.Div(
                    className='offset-by-one-third column two columns',
                    children=[
                        html.Button(
                            'Submit',
                            id='shopping-submit-list',
                        )
                    ]
                ),
                html.Div(
                    className='two columns',
                    children=[
                        html.Button(
                            'Clear',
                            id='shopping-clear-list',
                        )
                    ]
                ),
                html.Div(
                    className='three columns',
                    children=[
                        dbc.Alert(
                            id='shopping-status-alert',
                            duration=10000,
                            fade=True,
                        ),
                    ]
                ),
            ]
        ),
    ]
)


@app.callback(
    Output('shopping-shops-store', 'data'),
    [Input('shopping-shops-store', 'modified_timestamp')],
    [State('shopping-shops-store', 'data')],
)
def init_shops_store(last_modified, data):
    logger.debug("Updating saved Stores in Database...")
    return [html.Option(value=val) for val in sql_data.get_unique_shopping_shops().Shop]


@app.callback(
    Output('shopping-shops-list', 'children'),
    [Input('shopping-shops-store', 'data')]
)
def get_shopping_shops(data):
    logger.debug("Shops from store requested...")
    return data


@app.callback(
    Output('shopping-products-store', 'data'),
    [Input('shopping-products-store', 'modified_timestamp')],
    [State('shopping-products-store', 'data')],
)
def init_products_store(last_modified, data):
    logger.debug("Updating saved Items in Database...")
    return [html.Option(value=val) for val in sql_data.get_unique_shopping_items().Product]


@app.callback(
    Output('shopping-items-list', 'children'),
    [Input('shopping-products-store', 'data')],
)
def get_shopping_products(data):
    return data


@app.callback(
    Output('shopping-add-items-list', 'children'),
    [Input('shopping-new-item-button', 'n_clicks'),
     Input({'type': 'shopping-remove-item', 'id': ALL}, 'n_clicks')],
    [State('shopping-add-items-list', 'children')]
)
def shopping_manage_items(n_clicks, indexes, old_shopping_add_list):
    logger.info("Update Shopping items list called.")
    logger.info(f"      Indexes: {indexes}.")

    if any(indexes):
        # Remove item from list
        list_items_to_remove = [idx for idx, value in enumerate(indexes) if value]
        for index in list_items_to_remove:
            old_shopping_add_list.pop(index)
        return old_shopping_add_list

    if n_clicks is None:
        raise PreventUpdate

    # Add a new list item
    return old_shopping_add_list + [
        html.Div(
            className='row add__items',
            children=[
                html.Div(
                    className='offset-by-two two columns',
                    children=[
                        dcc.Input(
                            id={
                                'type': 'shopping-new-item',
                                'id': n_clicks+N_SHOPPING_ITEMS-1,
                            },
                            placeholder="Item...",
                            list='shopping-items-list',
                        )
                    ]
                ),
                html.Div(
                    className='two columns',
                    children=[
                        dcc.Input(
                            id={
                                'type': 'shopping-new-item-price',
                                'id': n_clicks+N_SHOPPING_ITEMS-1,
                            },
                            placeholder="Item Price...",
                            type='number',
                        )
                    ]
                ),
                html.Div(
                    className='two columns',
                    children=[
                        dcc.Input(
                            id={
                                'type': 'shopping-new-item-note',
                                'id': n_clicks+N_SHOPPING_ITEMS-1,
                            },
                            placeholder="Note...",
                        )
                    ]
                ),
                html.Div(
                    className='offset-by-one column one column',
                    children=[
                        html.Button(
                            "Remove Item",
                            id={
                                'type': 'shopping-remove-item',
                                'id': n_clicks+N_SHOPPING_ITEMS-1,
                            },
                        )
                    ]
                ),
            ],
        ),
    ]


@app.callback(
    [Output('shopping-status-alert', 'children'),
     Output('shopping-status-alert', 'className'),
     Output('shopping-status-alert', 'is_open')],
    [Input('shopping-submit-list', 'n_clicks')],
    [State('shopping-new-list-date', 'date'),
     State('shopping-new-price', 'value'),
     State('shopping-new-shop', 'value'),
     State({'type': 'shopping-new-item', 'id': ALL}, 'value'),
     State({'type': 'shopping-new-item-price', 'id': ALL}, 'value'),
     State({'type': 'shopping-new-item-note', 'id': ALL}, 'value')]
)
def save_shopping_list(submit_clicks, date, price, shop, items, prices, notes):
    logger.debug(f"Save shopping list called. button clicks: {submit_clicks}.")
    logger.debug(f"Items: {date, price, shop, items, prices, notes}.")
    if submit_clicks is None:
        return "", "", False

    shopping_list_prelim = pd.DataFrame(data={
        'Date': datetime.strptime(date, '%Y-%m-%d') if date else None,
        'Payment': float(price) if price else None,
        'Shop': shop,
        'Product': items,
        'Price': prices,
        'Note': notes,
    })
    logger.debug(f"prelim: {shopping_list_prelim}.")
    shopping_list = shopping_list_prelim.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    shopping_list = shopping_list_prelim.dropna(subset=['Product', 'Price'], how='all')
    logger.debug(f"after drop: {shopping_list}.")
    if shopping_list.empty:
        return "Pelase add at least one product to the list.", "shopping_status_alert_warning", True

    bad_entry_list = []
    if shopping_list.Date.isna().any():
        bad_entry_list.append(html.Li("Date is missing."))
    if shopping_list.Payment.isna().any():
        bad_entry_list.append(html.Li("Sum total is missing."))
    if shopping_list.Shop.isna().any():
        bad_entry_list.append(html.Li("Shop is missing."))
    if shopping_list.Product.isna().any():
        missing_products = shopping_list.Product.isna()
        bad_prices = [str(pproduct) for pproduct in shopping_list.Price[missing_products].tolist()]
        bad_entry_list.append(html.Li("These Products' price is missing: " + ", ".join(bad_prices)))
    if shopping_list.Price.isna().any():
        missing_prices = shopping_list.Price.isna()
        bad_products = [str(pprice) for pprice in shopping_list.Product[missing_prices].tolist()]
        bad_entry_list.append(html.Li("These Products' price is missing: " + ", ".join(bad_products)))

    if bad_entry_list:
        children = [html.H6("Can't add shopping list:"), html.Ul(bad_entry_list)]
        return children, "shopping_status_alert_fail", True
    else:
        logger.debug(f"Pandas Dataframe Shopping List: {shopping_list}")
        sql_data.add_shopping_list(shopping_list)
        return "Successfully added shopping list", "shopping_status_alert_success", True


@app.callback(
    [Output('shopping-new-price', 'value'),
     Output('shopping-new-shop', 'value'),
     Output({'type': 'shopping-new-item', 'id': ALL}, 'value'),
     Output({'type': 'shopping-new-item-price', 'id': ALL}, 'value'),
     Output({'type': 'shopping-new-item-note', 'id': ALL}, 'value')],
    [Input('shopping-clear-list', 'n_clicks')],
    [State({'type': 'shopping-new-item', 'id': ALL}, 'value'),
     State('shopping-save-clear-clicks', 'data')]
)
def clear_shopping_list(n_clicks, items, old_clicks):
    logger.info(f"Clear Shopping item values called. clicks: new: {n_clicks} old: {old_clicks}.")
    if n_clicks is None or n_clicks <= old_clicks['clicks']:
        raise PreventUpdate
    empty = ['' for _ in items]
    return '', '', empty, empty, empty


@app.callback(
    Output('shopping-save-clear-clicks', 'data'),
    [Input('shopping-clear-list', 'n_clicks')],
)
def init_shopping_clear_clicks_store(n_clicks):
    logger.debug(f"Clicks store: click {n_clicks}")
    if n_clicks is None:
        return {'clicks': 0}
    else:
        return {'clicks': n_clicks}
