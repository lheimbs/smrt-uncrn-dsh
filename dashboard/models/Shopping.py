#!/usr/bin/env python3

from sqlalchemy import ForeignKey
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import Table
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship

from models.db import Base


association_table = Table(
    'association',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('item.id')),
    Column('list_id', Integer, ForeignKey('list.id'))
)

class List(Base):
    __tablename__ = 'list'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    shop_id = Column(Integer, ForeignKey('shop.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))

    items = relationship(
        'Item',
        secondary=association_table,
        back_populates='lists',
    )
    shop = relationship('Shop')
    category = relationship('Category')

    def __repr__(self):
        return (
            f"<List(id={self.id}, "
            f"date={self.date}, "
            f"price={self.price}, "
            f"shop='{self.shop}', "
            f"category='{self.category}', "
            f"items={[item for item in self.items]})>"
        )


class Item(Base):
    __tablename__ = 'item'
    __table_args__ = (
        UniqueConstraint(
            'name',
            'price',
            'volume',
            'price_per_volume',
            'sale',
            'note',
            name='_unique_item_uc'
        ),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(String)
    price_per_volume = Column(String)
    sale = Column(Boolean)
    note = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))

    lists = relationship(
        'List',
        secondary=association_table,
        back_populates='items'
    )
    category = relationship('Category')

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


class Shop(Base):
    __tablename__ = 'shop'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    shop_id = Column(Integer, ForeignKey('shop.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship('Category')

    def __repr__(self):
        return (
            f"<Shop(id={self.id}, "
            f"name='{self.name}', "
            f"category='{self.category}')>"
        )


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
