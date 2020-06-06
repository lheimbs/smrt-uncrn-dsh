#!/usr/bin/env python3

from dashboard.app import db

association_table = db.Table(
    'association',
    db.Model.metadata,
    db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('list_id', db.Integer, db.ForeignKey('list.id'))
)


class List(db.Model):
    __tablename__ = 'list'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    items = db.relationship(
        'Item',
        secondary=association_table,
        back_populates='lists',
    )
    shop = db.relationship('Shop')
    category = db.relationship('Category')

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'price': self.price,
            'shop': self.shop.to_dict(),
            'category': self.category.to_dict() if self.category else self.category,
            'items': [item.to_dict() for item in self.items],
        }

    def __repr__(self):
        return (
            f"<List(id={self.id}, "
            f"date={self.date}, "
            f"price={self.price}, "
            f"shop='{self.shop}', "
            f"category='{self.category}', "
            f"items={[item.name for item in self.items]})>"
        )


class Item(db.Model):
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
    # category_name = db.Column(db.String, db.ForeignKey('category.name'))

    lists = db.relationship(
        'List',
        secondary=association_table,
        back_populates='items'
    )
    category = db.relationship('Category')

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


class Shop(db.Model):
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


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {
            'name': self.name,
        }

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
