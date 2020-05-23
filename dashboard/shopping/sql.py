#!/usr/bin/env python3

import logging
from datetime import datetime

import pandas as pd

from app import db
from models.Shopping import List, Shop

logger = logging.getLogger()


def get_shopping_expenses_by_date(start, end=None):
    logger.debug(f"Get expenses from 'shopping' table between {start} and {end}.")

    data = pd.read_sql(
        "SELECT DISTINCT Date, Price FROM 'list' WHERE Date BETWEEN ? AND ? ORDER BY Date;",
        db.engine,
        parse_dates=['date'],
        params=(start, end if end else datetime.now())
    )
    return data.groupby('date').sum().reset_index()


def get_unique_shopping_days():
    logger.debug("Get unique days in table 'shopping'.")
    days = pd.read_sql(
        "SELECT DISTINCT Date FROM list ORDER BY DATE",
        db.engine,
        parse_dates=['date']
    ).set_index('date')
    return days


def get_unique_shopping_shops():
    logger.debug("Get unique Shops from table 'shopping'.")
    shops = pd.read_sql(
        "SELECT DISTINCT name FROM shop",
        con=db.engine,
    )
    return shops


def get_unique_shopping_items():
    logger.debug("Get unique Products from table 'shopping'.")
    items = pd.read_sql(
        "SELECT DISTINCT name FROM item",
        con=db.engine,
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
    logger.info(f"{date, price, shop, items}")
    return True, ''
