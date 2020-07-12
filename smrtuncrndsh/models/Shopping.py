#!/usr/bin/env python3
from sqlalchemy.ext.associationproxy import association_proxy

from . import db, BaseMixin


class Liste(db.Model, BaseMixin):
    __tablename__ = 'liste'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    shop = db.relationship('Shop')
    category = db.relationship('Category')

    items = association_proxy('liste_items', 'item')

    def __init__(self, date, price, shop, category=None):
        self.date = date
        self.price = price
        self.shop = shop
        self.category = category

    def __repr__(self):
        return (
            f"<Liste(id={self.id}, "
            f"date={self.date}, "
            f"price={self.price}, "
            f"shop='{self.shop}', "
            f"category='{self.category}', "
            f"items={[item.name for item in self.items]})>"
        )

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'price': self.price,
            'shop': self.shop.to_dict(),
            'category': self.category.to_dict() if self.category else self.category,
            'items': [item.to_dict() for item in self.items],
        }


class ListeItem(db.Model, BaseMixin):
    __tablename__ = 'liste_item'

    id = db.Column(db.Integer, primary_key=True)
    liste_id = db.Column(db.Integer, db.ForeignKey('liste.id'))  # , primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))  # , primary_key=True)
    special_key = db.Column(db.String(50))

    # bidirectional attribute/collection of "liste"/"liste_items"
    liste = db.relationship(
        Liste,
        backref=db.backref(
            "liste_items",
            cascade="all, delete-orphan"
        )
    )

    # reference to the "Keyword" object
    item = db.relationship("Item")

    def __init__(self, item=None, liste=None, special_key=None):
        self.liste = liste
        self.item = item
        self.special_key = special_key


class Item(db.Model, BaseMixin):
    __tablename__ = 'item'
    __table_args__ = (
        db.UniqueConstraint(
            'name',
            'price',
            'volume',
            'price_per_volume',
            'sale',
            'note',
            'amount',
            name='_unique_item_uc'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.String)
    price_per_volume = db.Column(db.String)
    sale = db.Column(db.Boolean)
    note = db.Column(db.String)
    amount = db.Column(db.Integer, default=1)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category')

    def __init__(self, name, price, volume=None, price_per_volume=None, sale=False, note=None, amount=1, category=None):
        self.name = name
        self.price = price
        self.volume = volume
        self.price_per_volume = price_per_volume
        self.note = note
        self.sale = sale
        self.amount = amount
        self.category = category

    def __repr__(self):
        return (
            f"<Item(id={self.id}, "
            f"name='{self.name}', "
            f"price={self.price}, "
            f"volume='{self.volume}', "
            f"price_per_volume='{self.price_per_volume}', "
            f"sale={self.sale}, "
            f"note='{self.note}', "
            f"category='{self.category}')>"
        )

    def to_dict(self):
        return {
            'name': self.name,
            'price': self.price,
            'volume': self.volume,
            'price_per_volume': self.price_per_volume,
            'sale': self.sale,
            'note': self.note,
            'category': self.category.to_dict() if self.category else self.category,
        }


class Shop(db.Model, BaseMixin):
    __tablename__ = 'shop'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    # category_name = db.Column(db.String, db.ForeignKey('category.name'))
    category = db.relationship('Category')

    def to_dict(self):
        return {
            'name': self.name,
            'category': self.category.to_dict() if self.category else self.category,
        }

    def __repr__(self):
        return (
            f"<Shop(id={self.id}, "
            f"name='{self.name}', "
            f"category='{self.category}')>"
        )


class Category(db.Model, BaseMixin):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {
            'name': self.name,
        }

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
