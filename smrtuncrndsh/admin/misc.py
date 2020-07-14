from flask import current_app
from sqlalchemy import func

from ..models import db
from ..models.Shopping import Liste


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
