from flask import current_app
from sqlalchemy import func
from sqlalchemy.sql import sqltypes

from ..models import db
from ..models.Shopping import Liste, Category, Shop


def get_multiple_items(liste):
    """ Count items in liste.items and return all the occur more than once. """
    multiple = {}
    for item in liste.items:
        amount = liste.items.count(item)
        if amount > 1:
            multiple.update({item.id: amount})
    return multiple


def add_remove_items_from_liste(new_items, repeated_items, liste=None):
    """ Repeated items dont show up in the form of a QuerySelectMultipleField (new_items).
        To add multiple items to the Liste.items list repeated items are counted using js (repeated_items).
        This handles the adding/removing of all items.
    """
    add_items = []
    for item in new_items:
        if item.id in repeated_items.keys() and new_items.count(item) < repeated_items[item.id]:
            current_app.logger.debug(f"Add {repeated_items[item.id] - new_items.count(item)} items of {item.id}")
            for _ in range(repeated_items[item.id] - new_items.count(item)):
                add_items.append(item)
    new_items += add_items

    # remove deleted items or add new items to actual database
    for item in liste.items:
        db_count = liste.items.count(item)
        new_count = new_items.count(item)
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
        if not hasattr(obj, vals['data']):
            continue
        elif not vals['searchable'] and not vals['orderable']:
            continue
        elif not req_dict['search'] and not vals['search_value']:
            continue

        if vals['data'] == 'category':
            attr = getattr(Category, 'name')
            query = query.join(obj.category)
        elif vals['data'] == 'shop':
            attr = getattr(Shop, vals['data'], 'name')
            query = query.join(obj.shop)
        else:
            attr = getattr(obj, vals['data'])

        if isinstance(attr.property.columns[0].type, sqltypes.String):
            search = func.lower(req_dict['search'])
            search_value = func.lower(vals['search_value'])
            if req_dict['search'] and vals['searchable']:
                query = query.filter(func.lower(attr).contains(search))
            if vals['search_value'] and vals['searchable']:
                query = query.filter(func.lower(attr).contains(search_value))
        else:
            search = req_dict['search']
            search_value = vals['search_value']

            if req_dict['search'] and vals['searchable']:
                query = query.filter(attr == search)
            if vals['search_value'] and vals['searchable']:
                query = query.filter(attr == search_value)
    return query


def get_datatables_order_query(obj, req_dict, query):
    if req_dict and req_dict['columns'][req_dict['order_col']]['orderable']:
        if req_dict['order'] == 'asc':
            attr = getattr(obj, req_dict['columns'][req_dict['order_col']]['data']).asc()
        else:
            attr = getattr(obj, req_dict['columns'][req_dict['order_col']]['data']).desc()
        query = query.order_by(attr)
    return query
