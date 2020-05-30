#!/usr/bin/env python3

import logging
from datetime import datetime

from sqlalchemy import exc

# page import here, to get the supplied log level in modules (# noqa E420?)
from ..app import db
from models.Shopping import List, Shop, Category, Item

logger = logging.getLogger()


def generate_shopping_data():
    cat = Category(name='Lebensmittel')
    shop = Shop(name='REWE', category=cat)
    items = [
        Item(name='Bier', price=1.09, volume='', price_per_volume='', sale=False, note=''),
        Item(name='Pfand', price=0.08, volume='', price_per_volume='', sale=False, note=''),
        Item(name='Leergut', price=0.08, volume='', price_per_volume='', sale=False, note=''),
        Item(name='Kinder Bueno', price=1.99, volume='', price_per_volume='', sale=True, note=''),
        Item(name='Schokobons', price=1.99, volume='200g', price_per_volume='', sale=False, note=''),
        Item(name='Eis Stiel-Brownie', price=1.69, volume='', price_per_volume='', sale=False, note=''),
    ]
    list_1 = List(date=datetime(2020, 5, 16, 0, 0), price=6.76, shop=shop, items=items)

    list_2 = List(date=datetime(2019, 5, 15, 0, 0), price=3.61, shop=Shop(name='EDEKA', category=cat), items=[
        Item(name='Toast', price=0.59, volume='', price_per_volume='', sale=False, note=''),
        Item(name='Schokobons klein', price=1.99, volume='', price_per_volume='', sale=False, note=''),
        Item(name='Joghurt', price=0.88, volume='', price_per_volume='', sale=False, note='0,15'),
        Item(name='Pfand', price=0.15, volume='', price_per_volume='', sale=False, note='')
    ])

    try:
        db.session.add(list_1)
        db.session.add(list_2)
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
