#!/usr/bin/env python3
from datetime import datetime

import pandas as pd
from flask import current_app

from ...models import db
from ...models.Shopping import Shop, List, Item, Category


def is_data_in_shopping_tables():
    if all([Shop.query.count(), List.query.count(), Item.query.count(), Category.query.count()]):
        return True
    return False


def get_shopping_expenses_by_date(start, end=None):
    current_app.logger.debug(f"Get Lists unique days and prices between {start} and {end} from database.")

    if not end:
        end = datetime.now()

    prelim_data = db.session.query(
        List.date, List.price
    ).distinct().filter(List.date.between(start, end)).order_by(List.date)
    data = pd.DataFrame(prelim_data, columns=['date', 'price'])

    return data.groupby('date').sum().reset_index()


def get_all_lists():
    return List.query


def get_unique_shopping_days():
    current_app.logger.debug("Get unique List days from database.")
    days = pd.DataFrame(
        db.session.query(List.date).distinct().order_by(List.date),
        columns=['date'],
    ).set_index('date')
    return days


def get_shopping_expenses_per_shop(shop):
    current_app.logger.debug(f"Get expenses for shop {shop} from 'shopping' table.")
    expense = pd.DataFrame(
        db.session.query(
            List.date, List.price
        ).filter(
            List.shop == db.session.query(Shop).filter(
                Shop.name == shop
            ).scalar()
        ).all()
    )
    expense_gouped = expense.groupby('date')['price'].sum().rename(shop)
    return expense_gouped


def get_unique_shopping_shops():
    current_app.logger.debug("Get unique Shop names from database.")
    shops = pd.DataFrame(
        db.session.query(Shop.name).distinct().order_by(Shop.name),
        columns=['name'],
    )
    return shops
