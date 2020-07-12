#!/usr/bin/env python3
from datetime import datetime

import pandas as pd
from flask import current_app

from ...models import db
from ...models.Shopping import Shop, Liste, Item, Category


def is_data_in_shopping_tables():
    if all([Shop.query.count(), Liste.query.count(), Item.query.count(), Category.query.count()]):
        return True
    return False


def get_shopping_expenses_by_date(start, end=None):
    current_app.logger.debug(f"Get Lists unique days and prices between {start} and {end} from database.")

    if not end:
        end = datetime.now()

    prelim_data = db.session.query(
        Liste.date, Liste.price
    ).distinct().filter(Liste.date.between(start, end)).order_by(Liste.date)
    data = pd.DataFrame(prelim_data, columns=['date', 'price'])
    data['date'] = data['date'].apply(lambda date: datetime.combine(date, datetime.min.time()))
    return data.groupby('date').sum().reset_index()


def get_all_lists():
    return Liste.query


def get_unique_shopping_days():
    current_app.logger.debug("Get unique Liste days from database.")
    days = pd.DataFrame(
        db.session.query(Liste.date).distinct().order_by(Liste.date),
        columns=['date'],
    ).set_index('date')
    return days


def get_shopping_expenses_per_shop(shop):
    current_app.logger.debug(f"Get expenses for shop {shop} from 'shopping' table.")
    expense = pd.DataFrame(
        db.session.query(
            Liste.date, Liste.price
        ).filter(
            Liste.shop == db.session.query(Shop).filter(
                Shop.name == shop
            ).scalar()
        ).all()
    )
    if expense.empty:
        return expense
    return expense.groupby('date')['price'].sum().rename(shop)


def get_unique_shopping_shops():
    current_app.logger.debug("Get unique Shop names from database.")
    shops = pd.DataFrame(
        db.session.query(Shop.name).distinct().order_by(Shop.name),
        columns=['name'],
    )
    return shops
