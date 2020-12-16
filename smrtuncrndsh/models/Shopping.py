#!/usr/bin/env python3
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import func

from . import db, BaseMixin


class Category(db.Model, BaseMixin):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {
            'name': self.name,
        }

    def to_ajax(self):
        return {
            'edit': '',
            'delete': '',
            'id': self.id,
            'name': self.name,
        }

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

    def get_category(category: str):
        return Category.query.filter(func.lower(Category.name) == category.lower()).first()

    def exists(self):
        return db.session.query(Category.query.filter_by(
            name=self.name,
        ).exists()).scalar()


class Shop(db.Model, BaseMixin):
    __tablename__ = 'shop'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    # category_name = db.Column(db.String, db.ForeignKey('category.name'))
    category = db.relationship('Category', backref='shops')

    def to_dict(self):
        return {
            'name': self.name,
            'category': self.category.to_dict() if self.category else self.category,
        }

    def to_ajax(self):
        return {
            'edit': '',
            'delete': '',
            'id': self.id,
            'name': self.name,
            'category': self.category.name if self.category else '-',
        }

    def __repr__(self):
        return (
            f"<Shop(id={self.id}, "
            f"name='{self.name}', "
            f"category='{self.category}')>"
        )

    def get_shop(shop: str, category_name: str = "", category_obj: Category = None):
        shop_query = Shop.query.filter(func.lower(Shop.name) == shop.lower())
        if category_name:
            shop_query = shop_query.join(Shop.category).filter(func.lower(Category.name) == category_name.lower())
        elif category_obj:
            shop_query = shop_query.join(Shop.category).filter(Shop.category == category_obj)
        return shop_query.all()

    def exists(self):
        return db.session.query(Shop.query.filter_by(
            name=self.name,
            category_id=self.category_id,
        ).exists()).scalar()


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
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref='items')

    def __init__(
        self, name, price, volume=None, price_per_volume=None,
        sale=False, note=None, category=None
    ):
        self.name = name
        self.price = price
        self.volume = volume
        self.price_per_volume = price_per_volume
        self.note = note
        self.sale = sale
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
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'volume': self.volume,
            'price_per_volume': self.price_per_volume,
            'sale': self.sale,
            'note': self.note,
            'category': self.category.to_dict() if self.category else self.category,
        }

    def to_ajax(self):
        return {
            'edit': '',
            'delete': '',
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'volume': self.volume if self.volume else "-",
            'price_per_volume': self.price_per_volume if self.price_per_volume else "-",
            'sale': self.sale if self.sale else "-",
            'note': self.note if self.note else "-",
            'category': self.category.name if self.category else '-',
        }

    def exists(self):
        return db.session.query(Item.query.filter_by(
            name=self.name,
            price=self.price,
            volume=self.volume,
            price_per_volume=self.price_per_volume,
            sale=self.sale,
            note=self.note,
            category_id=self.category_id,
        ).exists()).scalar()

    def get_item(
        name: str,
        price: float,
        volume: str = "",
        price_per_volume: str = "",
        sale: bool = False,
        category_name: str = "",
        category_obj: Category = None
    ):
        item_query = Item.query.filter(func.lower(Item.name) == name.lower()).filter(Item.price == price)
        if volume:
            item_query = item_query.filter(Item.volume == volume)
        if price_per_volume:
            item_query = item_query.filter(Item.price_per_volume == price_per_volume)
        if sale:
            item_query = item_query.filter(Item.sale == sale)
        if category_name:
            item_query = item_query.join(Item.category).filter(func.lower(Category.name) == category_name.lower())
        elif category_obj:
            item_query = item_query.join(Item.category).filter(Item.category == category_obj)
        return item_query.all()


class Liste(db.Model, BaseMixin):
    __tablename__ = 'liste'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    user = db.relationship('User', backref='lists')
    shop = db.relationship('Shop', backref='lists')
    category = db.relationship('Category', backref='lists')

    items = association_proxy('liste_items', 'item')

    def __init__(self, date, price, shop, category=None):
        self.date = date
        self.price = price
        self.shop = shop
        self.category = category

    def __repr__(self):
        return (
            f"<Liste(id={self.id}, "
            f"user={self.user}, "
            f"date={self.date}, "
            f"price={self.price}, "
            f"shop='{self.shop}', "
            f"category='{self.category}', "
            f"items={[item.name for item in self.items]})>"
        )

    def to_ajax(self):
        return {
            'edit': '',
            'delete': '',
            'id': self.id,
            'user': self.user.name if self.user else '-',
            'date': self.date,
            'price': self.price,
            'shop': self.shop.name if self.shop else '-',
            'category': self.category.name if self.category else '-',
            'items': [item.name for item in self.items],
        }

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
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
    item = db.relationship("Item", backref='lists')

    def __init__(self, item=None, liste=None, special_key=None):
        self.liste = liste
        self.item = item
        self.special_key = special_key
