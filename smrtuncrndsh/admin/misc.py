import json
import dateutil.parser as dt
from datetime import timedelta

from flask import current_app
from sqlalchemy import func
from sqlalchemy.sql import sqltypes

from ..models import db
from ..models.Shopping import Liste, Category, Shop, Item
from ..models.Users import User


def get_multiple_items(liste):
    """ Count items in liste.items and return all the occur more than once. """
    multiple = {}
    for item in liste.items:
        amount = liste.items.count(item)
        if amount > 1:
            multiple.update({item.id: amount})
    return multiple


def add_remove_items_from_liste(new_items, repeated_items_raw, liste=None):
    """ Repeated items dont show up in the form of a QuerySelectMultipleField (new_items).
        To add multiple items to the Liste.items list repeated items are counted using js (repeated_items).
        This handles the adding/removing of all items.
    """
    # print(new_items, type(new_items), repeated_items_raw, type(repeated_items_raw))

    repeated_items = get_repeated_items(repeated_items_raw)
    if repeated_items_raw and not repeated_items:
        return False

    # print(new_items, type(new_items), repeated_items, type(repeated_items))

    add_items = []
    for item in new_items:
        if item.id in repeated_items.keys() and new_items.count(item) < repeated_items[item.id]:
            current_app.logger.debug(f"Add {repeated_items[item.id] - new_items.count(item)} items of {item.id}")
            for _ in range(repeated_items[item.id] - new_items.count(item)):
                current_app.logger.debug(f"Add item {item.name} (id: {item.id})")
                add_items.append(item)
    new_items += add_items

    # add new items or remove deleted items to actual database
    for item in liste.items:
        db_count = liste.items.count(item)
        new_count = new_items.count(item)
        # print(item.id, db_count, new_count)
        if db_count < new_count:
            for _ in range(new_count - db_count):
                current_app.logger.debug(f"Add <Item({item.id}, {item.name})> to list with id {liste.id}.")
                liste.items.append(item)
        elif db_count > new_count:
            for _ in range(db_count - new_count):
                current_app.logger.debug(f"Remove <Item({item.id}, {item.name})> from list with id {liste.id}.")
                liste.items.remove(item)

    for item in new_items:
        db_count = liste.items.count(item)
        new_count = new_items.count(item)
        # print(item.id, db_count, new_count)
        if db_count < new_count:
            for _ in range(new_count - db_count):
                current_app.logger.debug(f"Add <Item({item.id}, {item.name})> to list with id {liste.id}.")
                liste.items.append(item)
        elif db_count > new_count:
            for _ in range(db_count - new_count):
                current_app.logger.debug(f"Remove <Item({item.id}, {item.name})> from list with id {liste.id}.")
                liste.items.remove(item)

    if not liste.items and new_items:
        liste.items = new_items
    return True


def get_repeated_items(repeated_items):
    if isinstance(repeated_items, dict):
        return repeated_items

    try:
        repeated_items = json.loads(repeated_items.replace("'", '"'))
    except json.decoder.JSONDecodeError:
        current_app.logger.error(f"Coud not json-decode repeated_items '{repeated_items}'!")
        repeated_items = {}

    new_repeated_items = {}
    for key, value in repeated_items.items():
        try:
            new_repeated_items[int(key)] = value
        except ValueError:
            current_app.logger.debug(f"Key '{key}' is not a valid id. Skipping.")
    return new_repeated_items


def min_price():
    return db.session.query(func.min(Liste.price)).scalar()


def max_price():
    return db.session.query(func.max(Liste.price)).scalar()


def min_date():
    return db.session.query(func.min(Liste.date)).scalar()


def max_date():
    return db.session.query(func.max(Liste.date)).scalar()


def get_bool_from_string(bool_string):
    return True if bool_string == 'true' else False


def get_request_dict(request):
    request_dict = {}
    for key, val in request.items():
        if key in ['start', 'draw', 'length']:
            request_dict[key] = int(val)
        elif key == 'order[0][column]':
            request_dict['order_col'] = int(val)
        elif key == 'order[0][dir]':
            request_dict['order'] = val
        elif key == 'search[regex]':
            request_dict['regex'] = get_bool_from_string(val)
        elif key == 'search[value]':
            request_dict['search'] = val
        elif key.startswith('columns['):
            if 'columns' not in request_dict:
                request_dict['columns'] = {}

            key = key.replace('columns[', '')
            new_key = int(key[:key.find(']')])
            if new_key not in request_dict['columns'].keys():
                request_dict['columns'][new_key] = {}

            key = key.replace(f'{new_key}][', '').replace('][', '_')[:-1]
            if val in ('true', 'false'):
                request_dict['columns'][new_key][key] = get_bool_from_string(val)
            else:
                request_dict['columns'][new_key][key] = val
    return request_dict


def get_datatables_search_query(obj, req_dict):
    query = obj.query

    for col, vals in req_dict['columns'].items():
        vals['data'] = vals['data'].replace('[</br>]', '') if vals['data'].endswith('[</br>]') else vals['data']
        if not hasattr(obj, vals['data']):
            # current_app.logger.debug(f"Object <{obj}> has no attribute '{vals['data']}'.")
            continue
        elif not vals['searchable'] and not vals['orderable']:
            # current_app.logger.debug(f"'{vals['data']}' is not searchable AND orderable.")
            continue
        elif not req_dict['search'] and not vals['search_value']:
            # current_app.logger.debug(f"No search value provided for column '{vals['data']}'.")
            continue

        # if the searching object has relationships, these objects have to be translated here
        attr, query = get_attr_based_on_category(vals['data'], query, obj)

        if vals['data'] == 'items':
            search_req = req_dict['search'].lower()
            search = vals['search_value'].lower()
            query = search_items_string(query, search_req, vals['searchable'])
            query = search_items_string(query, search, vals['searchable'])
        elif isinstance(attr.property.columns[0].type, sqltypes.String):
            search_req = req_dict['search'].lower()
            search = vals['search_value'].lower()
            query = search_string(attr, query, search_req, vals['searchable'])
            query = search_string(attr, query, search, vals['searchable'])
        elif isinstance(attr.property.columns[0].type, sqltypes.DateTime):
            query = search_date(attr, query, req_dict['search'], vals['searchable'])
            query = search_date(attr, query, vals['search_value'], vals['searchable'])
        elif isinstance(attr.property.columns[0].type, sqltypes.Date):
            query = search_date_range(attr, query, req_dict['search'], vals['searchable'])
            query = search_date_range(attr, query, vals['search_value'], vals['searchable'])
        elif isinstance(attr.property.columns[0].type, sqltypes.Float):
            query = search_num_range(attr, query, req_dict['search'], vals['searchable'])
            query = search_num_range(attr, query, vals['search_value'], vals['searchable'])
        else:
            search = req_dict['search']
            search_value = vals['search_value']

            if req_dict['search'] and vals['searchable']:
                query = query.filter(attr == search)
            if vals['search_value'] and vals['searchable']:
                query = query.filter(attr == search_value)
    return query


def get_attr_based_on_category(category, query, obj):
    if category == 'category':
        attr = getattr(Category, 'name')
        query = query.join(obj.category)
    elif category == 'shop':
        attr = getattr(Shop, 'name')
        query = query.join(obj.shop)
    elif category == 'user':
        attr = getattr(User, 'name')
        query = query.join(obj.user)
    else:
        attr = getattr(obj, category)
    return attr, query


def search_string(attr, query, search_val, searchable):
    if search_val and searchable:
        query = query.filter(func.lower(attr).contains(search_val))
    return query


def search_items_string(query, search_val, searchable):
    if search_val and searchable:
        query = query.filter(Liste.items.any(func.lower(Item.name).contains(search_val)))
    return query


def search_date(attr, query, search_val, searchable):
    if search_val and searchable:
        search_start = dt.parse(search_val)
        search_end = search_start + timedelta(hours=24)
        query = query.filter(attr.between(search_start, search_end))
    return query


def search_date_range(attr, query, search_val, searchable):
    if search_val and searchable:
        search_start, search_end = search_val.split(' - ')
        search_start = dt.parse(search_start)
        search_end = dt.parse(search_end)
        query = query.filter(attr.between(search_start, search_end))
    return query


def search_num_range(attr, query, search_val, searchable):
    if search_val and searchable:

        search_vals = search_val.split(',')
        if len(search_vals) > 1:
            search_start = float(search_vals[0])
            search_end = float(search_vals[1])
            query = query.filter(attr >= search_start).filter(attr < search_end)
        else:
            query = query.filter(attr == search_val)
    return query


def get_datatables_order_query(obj, req_dict, query):
    if req_dict and req_dict['columns'][req_dict['order_col']]['orderable']:
        attr = getattr(obj, req_dict['columns'][req_dict['order_col']]['data'])

        if req_dict['columns'][req_dict['order_col']]['data'] == 'category':
            attr = getattr(Category, 'name')
            query = query.join(obj.category, isouter=True)

        try:
            attr_sorter = getattr(attr, req_dict['order'])
        except AttributeError:
            current_app.logger.warning(f"Can't sort by '{req_dict['order']}'. Sorting ascending instead.")
            attr_sorter = attr.asc
        query = query.order_by(attr_sorter())
    return query
