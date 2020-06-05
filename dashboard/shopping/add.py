#!/usr/bin/env python3

import logging

import numpy as np
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

from ..app import app
from . import sql

logger = logging.getLogger()

# constants
N_SHOPPING_ITEMS = 15
N_MAX_SHOPPING_ITEMS = 50


def generate_items_list(min_id, max_id):
    return [
        html.Div(
            className='row add__items',
            children=[
                html.Div(
                    className='offset-by-one two columns',
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
                    className='one column',
                    children=[
                        dcc.Input(
                            id={
                                'type': 'shopping-new-item-price',
                                'id': n,
                            },
                            placeholder="Price...",
                            type='number',
                        )
                    ]
                ),
                html.Div(
                    className='one column',
                    children=[
                        dcc.Input(
                            id={
                                'type': 'shopping-new-item-amount',
                                'id': n,
                            },
                            min=1,
                            value=1,
                            placeholder="Amount...",
                            type='number',
                        )
                    ]
                ),
                html.Div(
                    className='one column',
                    children=[
                        dcc.Input(
                            id={
                                'type': 'shopping-new-item-volume',
                                'id': n,
                            },
                            placeholder="Volume...",
                        )
                    ]
                ),
                html.Div(
                    className='one column',
                    children=[
                        dcc.Input(
                            id={
                                'type': 'shopping-new-item-ppv',
                                'id': n,
                            },
                            placeholder="€/Vol...",
                        )
                    ]
                ),
                html.Div(
                    className='one column',
                    children=[
                        dcc.Checklist(
                            id={
                                'type': 'shopping-new-item-sale',
                                'id': n,
                            },
                            options=[{'label': 'Sale', 'value': 'sale'}],
                            value=[],
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
                    className='one column',
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
        for n in range(min_id, max_id)
    ]


layout = html.Div(
    className='shopping__add__container',
    children=[
        dcc.Store(id='shopping-save-clear-clicks'),
        dcc.Store(id='shopping-add-categories-store'),
        dcc.Store(id='shopping-add-prelim-data-store'),
        dcc.Store(id='shopping-add-interim-data-store'),
        dcc.Store(id='shopping-add-final-data-store'),
        dcc.Store(id='shopping-add-added-lists'),
        dcc.Store(id='shopping-add-toggle-overlay-1'),
        dcc.Store(id='shopping-add-toggle-overlay-2'),
        dbc.Alert(
            id='shopping-status-alert',
            duration=10000 * 5,
            dismissable=True,
            fade=True,
            is_open=False,
        ),
        dbc.Alert(
            id='shopping-status-alert-2',
            duration=10000 * 5,
            dismissable=True,
            fade=True,
            is_open=False,
        ),
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
        html.Datalist(
            id='shopping-categories-list',
        ),
        html.Div(
            id='shopping-add-items-list',
            className='shopping__add__items',
            children=generate_items_list(0, N_SHOPPING_ITEMS),
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

                    ]
                ),
            ]
        ),
        html.Div(
            id='shopping-add-add-categories-overlay',
            className='overlay',
            children=[
                html.Button('Submit', n_clicks=1, id='shopping-add-add-categories-overlay-submit'),
                dcc.Input(id='shopping-add-shop-category')
            ]
        ),
    ]
)


@app.callback(
    Output('shopping-shops-store', 'data'),
    [Input('shopping-shops-store', 'modified_timestamp')],
    [
        State('shopping-shops-store', 'data'),
        State('error-store', 'data'),
    ]
)
def init_shops_store(last_modified, data, errors):
    logger.debug("Updating saved Stores in Database...")
    if errors['shop']:
        logger.warning("Shops table does not exist.")
        return []
    return [html.Option(value=val) for val in sql.get_unique_shopping_shops().name]


@app.callback(
    Output('shopping-add-categories-store', 'data'),
    [Input('shopping-add-categories-store', 'modified_timestamp')],
    [
        State('shopping-add-categories-store', 'data'),
        State('error-store', 'data'),
    ]
)
def init_categories_store(last_modified, data, errors):
    logger.debug("Updating saved Categories in Database...")
    if errors['category']:
        logger.warning("Categories table does not exist.")
        return []
    return [html.Option(value=val[0]) for val in sql.get_categories()]


@app.callback(
    Output('shopping-categories-list', 'children'),
    [Input('shopping-add-categories-store', 'data')],
)
def get_shopping_categories(data):
    return data


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
    [
        State('shopping-products-store', 'data'),
        State('error-store', 'data'),
    ],
)
def init_products_store(last_modified, data, errors):
    logger.debug("Updating saved Items in Database...")
    if errors['shop']:
        logger.warning("Items table does not exist.")
        return []
    return [html.Option(value=val) for val in sql.get_unique_shopping_items().name]


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
    logger.debug("Update Shopping items list called.")
    if any(indexes):
        # Remove item from list
        list_items_to_remove = [idx for idx, value in enumerate(indexes) if value]
        for index in list_items_to_remove:
            old_shopping_add_list.pop(index)
        return old_shopping_add_list

    if n_clicks is None or len(old_shopping_add_list) >= N_MAX_SHOPPING_ITEMS:
        raise PreventUpdate

    # Add a new list item
    return old_shopping_add_list + generate_items_list(
        n_clicks + N_SHOPPING_ITEMS - 1,
        n_clicks + N_SHOPPING_ITEMS
    )


@app.callback(
    Output('shopping-add-prelim-data-store', 'data'),
    [Input('shopping-submit-list', 'n_clicks')],
    [
        State('shopping-new-list-date', 'date'),
        State('shopping-new-price', 'value'),
        State('shopping-new-shop', 'value'),
        State({'type': 'shopping-new-item', 'id': ALL}, 'value'),
        State({'type': 'shopping-new-item-price', 'id': ALL}, 'value'),
        State({'type': 'shopping-new-item-amount', 'id': ALL}, 'value'),
        State({'type': 'shopping-new-item-volume', 'id': ALL}, 'value'),
        State({'type': 'shopping-new-item-ppv', 'id': ALL}, 'value'),
        State({'type': 'shopping-new-item-sale', 'id': ALL}, 'value'),
        State({'type': 'shopping-new-item-note', 'id': ALL}, 'value'),
        State('error-store', 'data')
    ]
)
def prepare_shopping_data(
    submit_clicks,
    date, price, shop, items, prices, amounts, volumes, ppvs, sales, notes,
    errors
):
    data_dict = {}
    if submit_clicks is None:
        raise PreventUpdate

    elif errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        data_dict.update(error=["Neccessary Shopping tables do not exist in database!"])
    else:
        logger.debug(f"Save shopping list called. List: {date, price, shop}. Button clicks: {submit_clicks}.")
        prices = [float(price) if price else None for price in prices]
        items_complete = pd.DataFrame(data={
            'name': items,
            'price': prices,
            'amount': amounts,
            'volume': volumes,
            'price_per_volume': ppvs,
            'sale': [True if sale else False for sale in sales],
            'note': notes,
        })
        # logger.debug(f"items before drop:\n{items_complete}.")
        shopping_list = items_complete.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        shopping_list = items_complete.dropna(subset=['name', 'price'], how='all')
        logger.debug(f"items after drop:\n{shopping_list}.")

        missing = []
        if not price:
            missing.append(html.Li("Please add a total Payment for this shopping list."))
        if not shop:
            missing.append(html.Li("Please add a shop for this shopping list."))
        if not date:
            missing.append(html.Li("Please select a date for this shopping list."))

        missing += parse_add_items(shopping_list)

        if missing:
            data_dict.update(error=missing)
        else:
            data_dict.update(
                data={
                    'price': price,
                    'shop': {'name': shop},
                    'date': date,
                    'items': shopping_list.to_dict('records')
                }
            )
    return data_dict


@app.callback(
    [
        Output('shopping-add-add-categories-overlay', 'children'),
        Output('shopping-add-toggle-overlay-1', 'data'),
        Output('shopping-add-interim-data-store', 'data'),
        Output('shopping-add-add-categories-overlay-submit', 'n_clicks'),
    ],
    [Input('shopping-add-prelim-data-store', 'data')],
    [State('shopping-add-add-categories-overlay', 'children')]
)
def handle_missing_categories(data, old_children):
    if not data:
        raise PreventUpdate

    if 'error' in data.keys():
        logger.debug("Errors detected with data, skipping categories check.")
        return old_children, None, data, 1

    logger.debug(f"Handle missing categories: {data}.")
    overlay_children = []
    missing_shop, missing_items = get_missing_categories(data['data'])

    overlay_children.append(
        html.Div(
            className='row',
            hidden=False if missing_shop else True,
            children=[
                html.H6(
                    f"Please select a category for shop '{data['data']['shop']['name']}':",
                    className='six columns'
                ),
                dcc.Input(
                    id='shopping-add-shop-category',
                    className='six columns',
                    placeholder='Category...',
                    list='shopping-categories-list'
                )
            ]
        )
    )

    for item in missing_items:
        div = html.Div(
            className='row',
            hidden=False if missing_items else True,
            children=[
                html.H6(
                    f"Please select a category for item '{item}':",
                    className='six columns'
                ),
                dcc.Input(
                    id={
                        'type': 'shopping-add-item-category',
                        'id': 'shopping-add-item-category-' + item,
                    },
                    className='six columns',
                    placeholder='Category...',
                    list='shopping-categories-list'
                )
            ]
        )
        overlay_children.append(div)
    overlay_children += [html.Br(), html.Hr(), html.Br()]
    overlay_children.append(
        html.Button(
            'Submit',
            n_clicks=0,
            id='shopping-add-add-categories-overlay-submit',
            className='offset-by-five two columns',
            style={'backgroundColor': 'var(--background)'},
        )
    )

    if missing_shop or missing_items:
        data['missing'] = {}
        if missing_items:
            data['missing'].update(items=missing_items)
        if missing_shop:
            data['missing'].update(shop=missing_shop)
        clicks = 0
    else:
        clicks = 1
    return overlay_children, None, data, clicks


@app.callback(
    [
        Output('shopping-add-final-data-store', 'data'),
        Output('shopping-add-toggle-overlay-2', 'data'),
    ],
    [
        Input('shopping-add-add-categories-overlay-submit', 'n_clicks'),
    ],
    [
        State('shopping-add-interim-data-store', 'data'),

        State('shopping-add-shop-category', 'value'),
        State({'type': 'shopping-add-item-category', 'id': ALL}, 'id'),
        State({'type': 'shopping-add-item-category', 'id': ALL}, 'value'),
    ]
)
def add_categories_to_list(save_clicks, data, shop_category, item_ids, item_categories):
    if not data or not save_clicks:
        logger.debug("Add categories to list - data or clicks none.")
        raise PreventUpdate
    elif 'missing' not in data.keys():
        logger.debug("No missing categories in shopping list. Closing overlay again.")
        return data, True
    elif 'error' in data.keys():
        logger.debug("Errors detected with data, skipping categories handling.")
        return data, True

    logger.debug(f"Add categories to shop/items.")
    if shop_category:
        data['data']['shop'].update(category=shop_category)

    if item_ids and item_categories and len(item_ids) == len(item_categories):
        for item, category in zip(item_ids, item_categories):
            for item_dict in data['data']['items']:
                if item_dict['name'] == item['id'].replace('shopping-add-item-category-', ''):
                    item_dict.update(category=category)
    return data, None


@app.callback(
    [
        Output('shopping-status-alert', 'children'),
        Output('shopping-status-alert', 'className'),
        Output('shopping-status-alert', 'is_open'),
        Output('shopping-add-added-lists', 'data'),
    ],
    [Input('shopping-add-final-data-store', 'data')],
    [
        State('shopping-add-added-lists', 'data'),
        State('shopping-add-add-categories-overlay-submit', 'n_clicks'),
    ]
)
def save_final_shopping_list_and_alert(data, added_lists, save_button_clicks):
    logger.debug(f"final save called.\ndata: {data}\nadded: {added_lists}")
    if not save_button_clicks:
        raise PreventUpdate

    if 'error' in data.keys():
        return (
            [html.H6('Error'), html.Hr(), html.Ul(data['error'])],
            'shopping_status_alert_fail',
            True,
            added_lists
        )
    else:
        success, infos = sql.add_shopping_list(data['data'])
        if success:
            if added_lists:
                added_lists.append(data['data'])
            else:
                added_lists = [data['data']]
            return (
                [html.H6('Success'), html.Hr(), html.Ul(infos)],
                'shopping_status_alert_success',
                True,
                added_lists
            )
        else:
            return (
                [html.H6('Error'), html.Hr(), html.Ul(infos)],
                'shopping_status_alert_fail',
                True,
                added_lists
            )


@app.callback(
    Output('shopping-add-add-categories-overlay', 'style'),
    [
        Input('shopping-add-toggle-overlay-1', 'data'),
        Input('shopping-add-toggle-overlay-2', 'data'),
    ],
    [
        State('shopping-add-add-categories-overlay', 'style'),
        State('shopping-add-interim-data-store', 'data'),
    ]
)
def update_categories_overlay_style(data_1, data_2, prev_style, data):
    if 'missing' not in data.keys():
        logger.debug("Hide overlay")
        return {'display': 'none'}

    if prev_style and 'display' in prev_style.keys():
        if prev_style['display'] == 'none':
            logger.debug("Display overlay")
            return {'display': 'block'}
        else:
            logger.debug("Hide overlay")
            return {'display': 'none'}
    else:
        logger.debug("Display overlay")
        return {'display': 'block'}


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
    logger.debug(f"Clear Shopping item values called. clicks: new: {n_clicks} old: {old_clicks}.")
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


def parse_add_items(shopping_list):
    missing = []

    if shopping_list.empty:
        missing.append(html.Li("Please supply at least one item with a price for this shopping list."))
    else:
        if shopping_list.name.isna().any():
            missing_products = shopping_list.name.isna()
            bad_prices = [str(pproduct) for pproduct in shopping_list.price[missing_products].tolist()]
            missing.append(html.Li("These Products' price is missing: " + ", ".join(bad_prices)))
        if shopping_list.price.isna().any():
            missing_prices = shopping_list.price.isna()
            bad_products = [str(pprice) for pprice in shopping_list.name[missing_prices].tolist()]
            missing.append(html.Li("These Products' price is missing: " + ", ".join(bad_products)))
        if shopping_list.amount.isna().any():
            missing_amounts = shopping_list.amount.isna()
            bad_products = [str(amount) for amount in shopping_list.name[missing_amounts].tolist()]
            missing.append(html.Li("These Products' amount is invalid: " + ", ".join(bad_products)))
    return missing


def get_missing_categories(data):
    missing_shop, missing_items = False, []
    if not sql.check_shop_has_category(data['shop']['name']):
        missing_shop = True

    for item in data['items']:
        if not sql.check_item_has_category(
            item['name'],
            item['price'],
            item['volume'] if item['volume'] else '',
            item['price_per_volume'] if item['price_per_volume'] else '',
            item['sale'],
            item['note'] if item['note'] else '',
        ):
            missing_items.append(item['name'])
    return missing_shop, missing_items


def check_missing_categories(list_obj):
    missing_shop = False
    if not list_obj.shop.category:
        missing_shop = True

    missing_items = []
    for item in list_obj.items:
        if not item.category:
            missing_items.append(item.id)
    return missing_shop, missing_items
