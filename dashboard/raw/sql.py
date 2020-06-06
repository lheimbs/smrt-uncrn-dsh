#!/usr/bin/env python3

import logging
import pandas as pd
from sqlalchemy import func, exc

from ..app import db
from models.Mqtt import Mqtt
from models.ProbeRequest import ProbeRequest
from models.RoomData import RoomData
from models.RfData import RfData
from models.Shopping import Item, Shop, Category, List

logger = logging.getLogger()


def get_mqtt_topics_as_options():
    topics = []
    for topic in db.session.query(Mqtt.topic).distinct().order_by(Mqtt.topic):
        topics.append({'label': topic.topic, 'value': topic.topic})
    return topics


def get_mqtt_messages_by_topic(topics, limit, start_date, end_date):
    query = Mqtt.query
    if topics:
        query = query.filter(Mqtt.topic.in_(topics))
    if start_date:
        query = query.filter(Mqtt.date >= start_date)
    if end_date:
        query = query.filter(Mqtt.date <= end_date)
    query = query.order_by(Mqtt.date.desc())
    if limit:
        query = query.limit(limit)

    messages_dict = []
    for message in query:
        message = message.to_dict()
        message.update({'time': message['date'].time()})
        message['date'] = message['date'].date()
        messages_dict.append(message)
    return pd.DataFrame(messages_dict, columns=['date', 'time', 'topic', 'payload', 'retain', 'qos'])


def get_raw_probes(limit, start_date, end_date):
    query = ProbeRequest.query
    if start_date:
        query = query.filter(ProbeRequest.date >= start_date)
    if end_date:
        query = query.filter(ProbeRequest.date <= end_date)
    query = query.order_by(ProbeRequest.date.desc())
    if limit:
        query = query.limit(limit)

    entries_list = []
    for entry in query:
        entry_dict = entry.to_dict()
        entry_dict.update(id=entry.id)
        entry_dict.update({'time': entry_dict['date'].time()})
        entry_dict['date'] = entry_dict['date'].date()
        entries_list.append(entry_dict)
    return pd.DataFrame(entries_list, columns=['date', 'time', 'macaddress', 'make', 'ssid', 'rssi'])


def get_raw_room_data(limit, start_date, end_date):
    query = RoomData.query
    if start_date:
        query = query.filter(RoomData.date >= start_date)
    if end_date:
        query = query.filter(RoomData.date <= end_date)
    query = query.order_by(RoomData.date.desc())
    if limit:
        query = query.limit(limit)

    entries_list = []
    for entry in query:
        entry_dict = entry.to_dict()
        entry_dict.update(id=entry.id)
        entry_dict.update({'time': entry_dict['date'].time()})
        entry_dict['date'] = entry_dict['date'].date()
        entries_list.append(entry_dict)
    return pd.DataFrame(entries_list, columns=[
        'date',
        'time',
        'temperature',
        'humidity',
        'pressure',
        'altitude',
        'brightness'
    ])


def get_raw_rf_data(limit, start_date, end_date):
    query = RfData.query
    if start_date:
        query = query.filter(RfData.date >= start_date)
    if end_date:
        query = query.filter(RfData.date <= end_date)
    query = query.order_by(RfData.date.desc())
    if limit:
        query = query.limit(limit)

    probes_dict = []
    for entry in query:
        entry_dict = entry.to_dict()
        entry_dict.update(id=entry.id)
        entry_dict.update({'time': entry_dict['date'].time()})
        entry_dict['date'] = entry_dict['date'].date()
        probes_dict.append(entry_dict)
    return pd.DataFrame(probes_dict, columns=[
        'date',
        'time',
        'decimal',
        'bits',
        'binary',
        'pulse_length',
        'protocol'
    ])


def get_raw_shopping_items(limit, search):
    query = Item.query
    if search:
        query = query.filter(func.lower(Item.name).like(f"%{search}%"))
    query = query.order_by(Item.name)
    if limit:
        query = query.limit(limit)

    entries_list = []
    for entry in query:
        if entry.category:
            category_name = entry.category.name
        else:
            category_name = ''
        entry_dict = entry.to_dict()
        entry_dict.update(category_name=category_name)
        entry_dict.update(id=entry.id)
        entry_dict.update(list_entrys=len(entry.lists))
        entries_list.append(entry_dict)
    return pd.DataFrame(entries_list, columns=[
        'id',
        'name',
        'price',
        'price_per_volume',
        'volume',
        'sale',
        'note',
        'category_name',
        'list_entrys'
    ])


def get_raw_shopping_shops(limit, search):
    query = Shop.query
    if search:
        query = query.filter(func.lower(Shop.name).like(f"%{search}%"))
    query = query.order_by(Shop.name)
    if limit:
        query = query.limit(limit)

    entries_list = []
    for entry in query:
        if entry.category:
            category_name = entry.category.name
        else:
            category_name = ''
        entry_dict = entry.to_dict()
        entry_dict.update(category_name=category_name)
        entry_dict.update(id=entry.id)
        entries_list.append(entry_dict)
    return pd.DataFrame(entries_list, columns=[
        'id',
        'name',
        'category_name',
    ])


def update_shop(data):
    shop_obj = Shop.query.filter(Shop.id == data['id']).scalar()
    shop_obj.name = data['name']
    new_category = None

    category_query = Category.query.filter(Category.name == data['category_name'])
    if category_query.count() == 1:
        shop_obj.category = category_query.scalar()
    elif category_query.count() > 1:
        logger.error(f"Category {data['category_name']} exists more than once!")
    else:
        logger.debug(f"Create new Category '{data['category_name']}'.")
        new_category = Category(name=data['category_name'])
        shop_obj.category = new_category

    try:
        if new_category:
            db.session.add(new_category)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        logger.error(e)
        db.session.rollback()
        return f"{data['name']}: {e}"
    return None


def update_items(data):
    logger.debug(f"Update item {data['name']}.")

    item_obj = Item.query.filter(Item.id == data['id']).scalar()
    item_status, _ = item_exists_already(data)

    if item_status:
        update_status, infos = False, [f"Item {item_obj.name} already exists."]
    else:
        item_obj.name = data['name']
        item_obj.price = data['price']
        item_obj.price_per_volume = data['price_per_volume']
        item_obj.volume = data['volume']
        item_obj.sale = data['sale']
        item_obj.note = data['note']

        new_category = None
        category_query = Category.query.filter(Category.name == data['category_name'])
        if category_query.count() == 1:
            item_obj.category = category_query.scalar()
        elif category_query.count() > 1:
            logger.error(f"Category {data['category_name']} exists more than once!")
        else:
            new_category = Category(name=data['category_name'])
            item_obj.category = new_category

        try:
            if new_category:
                db.session.add(new_category)
            db.session.commit()
            update_status, infos = True, [f"Successfully changed {data['name']}'s attributes."]
        except exc.IntegrityError:
            logger.warning("SqlAlchemy IntegrityError: Edited Item violates unique constraints.")
            logger.debug(item_obj)
            db.session.rollback()
            update_status, infos = False, ['Error: Item violates Integrity rules.']
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            update_status, infos = False, [
                f"Error: Could not change item {data['name']}.",
                'Error:',
                str(e)
            ]
    return update_status, infos


def item_exists_already(data):
    logger.debug(f'Check if item exists: {data}.')
    item_query = Item.query.filter(
        Item.name == data['name']
    ).filter(
        Item.price == data['price']
    ).filter(
        Item.price_per_volume == data['price_per_volume']
    ).filter(
        Item.volume == data['volume']
    ).filter(
        Item.sale == data['sale']
    ).filter(
        Item.note == data['note']
    )
    if item_query.count() > 0:
        return True, item_query
    return False, None


def update_list_with_changed_item(old_id, new_query):
    old_item = Item.query.filter(Item.id == old_id).scalar()
    new_item = new_query.scalar()

    logger.debug(f"Item {old_item.name} exists in {len(old_item.lists)} lists. Replacing it with new item in lists.")

    for old_items_list in old_item.lists:
        new_items_list = []
        for idx, list_item in enumerate(old_items_list.items):
            if list_item.id == old_item.id:
                new_items_list.append(new_item)
            else:
                new_items_list.append(list_item)
        old_items_list.items = new_items_list

    try:
        db.session.commit()
    except exc.SQLAlchemyError as e:
        logger.error(e)
        db.session.rollback()
        return False, [
            'Changing Item in its lists failed.',
            f"old item: {old_item}",
            f"new item: {new_item}"
        ]
    return True, ['Changing item in lists succeeded']


def get_shopping_lists(start, end):
    lists = List.query.filter(
        List.date.between(start, end)
    )
    lists = [shopping_list.to_dict() for shopping_list in lists]
    for shopping_list in lists:
        shopping_list['date'] = shopping_list['date'].isoformat()
    return lists
