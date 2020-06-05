#!/usr/bin/env python3

import logging
from datetime import datetime

import pandas as pd
from sqlalchemy import func, exc

from ..app import db
from models.Shopping import List, Shop, Item, Category

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


def get_categories():
    return db.session.query(Category.name).order_by(Category.name).all()


def get_list_object(date, price):
    return List(date=datetime.strptime(date, '%Y-%m-%d'), price=price)


def get_category_object(category_name):
    if not category_name:
        logger.debug("Category name is invalid.")
        return None

    cat_query = Category.query.filter(
        func.lower(Category.name) == category_name.lower()
    )
    if cat_query.count() > 1:
        logger.warning(f"Multiple categories named '{category_name}' exist! Selecting first available.")
        cat = cat_query.first()
    elif cat_query.count() == 1:
        cat = cat_query.scalar()
    else:
        logger.debug(f"No category named {category_name} exists. Creating new.")
        cat = Category(name=category_name)
        db.session.add(cat)
    return cat


def get_shop_object(shop_dict):
    shop_name = shop_dict['name']
    if 'category' in shop_dict.keys():
        cat = get_category_object(shop_dict['category'])
        shop_query = Shop.query.filter(
            func.lower(Shop.name) == shop_name.lower(),
            Shop.category_id == cat.id
        )
    else:
        cat = None
        shop_query = Shop.query.filter(
            func.lower(Shop.name) == shop_name.lower(),
        )

    if shop_query.count() > 1:
        logger.warning(f"Multiple shops named '{shop_name}' exist! Selecting first available.")
        shop = shop_query.first()
    elif shop_query.count() == 1:
        shop = shop_query.scalar()
    else:
        shop = Shop(name=shop_name)
        db.session.add(shop)
    
    if cat:
        shop.category = cat
    return shop


def get_item_object(item, price, volume, ppv, sale, note, cat):
    cat = get_category_object(cat)

    item_query = Item.query.filter(
        func.lower(Item.name) == item.lower(),
        Item.price == price,
        Item.volume == volume,
        Item.price_per_volume == ppv,
        Item.sale == sale,
        Item.note == note
    )
    if cat:
        item_query = item_query.filter(
            Item.category_id == cat.id
        )

    if item_query.count() > 1:
        logger.warning(f"Multiple items named '{item}' exist! Selecting first available.")
        item = item_query.first()
    elif item_query.count() == 1:
        item = item_query.scalar()
    else:
        item = Item(
            name=item,
            price=price,
            price_per_volume=ppv,
            volume=volume,
            sale=sale,
            note=note
        )
        db.session.add(item)
    
    if cat:
        item.category = cat
    return item


def check_shop_has_category(shop_name):
    shop_query = Shop.query.filter(func.lower(Shop.name) == shop_name.lower())
    if shop_query.count() > 1:
        logger.warning(f"Multiple shops named '{shop_name}' exist!")
        retVal = False
    elif shop_query.count() == 1:
        if shop_query.scalar().category.name:
            retVal = True
        else:
            retVal = False
    else:
        retVal = False
    return retVal


def check_item_has_category(item, price, volume, ppv, sale, note):
    item_query = Item.query.filter(
        func.lower(Item.name) == item.lower(),
        Item.price == price,
        Item.volume == volume,
        Item.price_per_volume == ppv,
        Item.sale == sale,
        Item.note == note
    )
    if item_query.count() > 1:
        logger.warning(f"Multiple items named '{item}' exist! Selecting first available.")
        has_cat = True if item_query.first().category else False
    elif item_query.count() == 1:
        has_cat = True if item_query.scalar().category else False
    else:
        has_cat = False
    return has_cat


def check_shop_exists(shop_name):
    shop_query = Shop.query.filter(func.lower(Shop.name) == shop_name.lower())
    if shop_query.count() > 1:
        logger.warning(f"Multiple shops named '{shop_name}' exist!")
        retVal = True
    elif shop_query.count() == 1:
        retVal = True
    else:
        retVal = False
    return retVal


def add_shopping_list(list_dict):
    logger.debug("Adding list to database.")
    list_obj = get_list_object(list_dict['date'], list_dict['price'])
    list_obj.shop = get_shop_object(list_dict['shop'])

    for item in list_dict['items']:
        name = item['name']
        price = item['price']
        amount = item['amount']
        volume = item['volume'] if item['volume'] else ''
        ppv = item['price_per_volume'] if item['price_per_volume'] else ''
        sale = item['sale']
        note = item['note'] if item['note'] else ''
        cat = item['category'] if 'category' in item.keys() else ''
        for _ in range(amount):
            list_obj.items.append(get_item_object(name, price, volume, ppv, sale, note, cat))

    infos = []
    try:
        db.session.add(list_obj)
        db.session.commit()
        update_status, infos = True, ["Successfully added Shopping List."]
    except exc.IntegrityError as error:
        logger.error(f"SqlAlchemy IntegrityError: {error}.")
        logger.debug(list_obj)
        db.session.rollback()
        update_status, infos = False, ['Error: List violates Integrity rules.']
    except exc.SQLAlchemyError as e:
        logger.error(e)
        db.session.rollback()
        update_status, infos = False, [
            "Error: Could not add Shopping List.",
            'Error:',
            str(e)
        ]
    return update_status, infos
