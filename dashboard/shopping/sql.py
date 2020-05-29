#!/usr/bin/env python3

import logging
from datetime import datetime

import pandas as pd

from ..app import db
from models.Shopping import List, Shop, Item

logger = logging.getLogger()


def get_shopping_expenses_by_date(start, end=None):
    logger.debug(f"Get Lists unique days and prices between {start} and {end} from database.")

    if not end:
        end = datetime.now()

    prelim_data = db.session.query(
        List.date, List.price
    ).distinct().filter(List.date.between(start, end)).order_by(List.date)
    data = pd.DataFrame(prelim_data, columns=['date', 'price'])

    return data.groupby('date').sum().reset_index()


def get_unique_shopping_days():
    logger.debug("Get unique List days from database.")
    days = pd.DataFrame(
        db.session.query(List.date).distinct().order_by(List.date),
        columns=['date'],
    ).set_index('date')
    return days


def get_unique_shopping_shops():
    logger.debug("Get unique Shop names from database.")
    shops = pd.DataFrame(
        db.session.query(Shop.name).distinct().order_by(Shop.name),
        columns=['name'],
    )
    return shops


def get_unique_shopping_items():
    logger.debug("Get unique Item names from database.")
    items = pd.DataFrame(
        db.session.query(Item.name).distinct().order_by(Item.name),
        columns=['name'],
    )
    return items


def get_shopping_expenses_per_shop(shop):
    logger.debug(f"Get expenses for shop {shop} from 'shopping' table.")
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


def get_recent_lists(min_date):
    return List.query.filter(List.date > min_date)


def get_all_lists():
    return List.query

def add_shopping_list(date, price, shop, items):
    date = datetime.strptime(date, '%Y-%m-%d')
    logger.info(f"{date, price, shop, items}")
    new_list = List(date=date, price=price)

    if Shop.query.filter(Shop.name):
        pass

    return True, ''
