#!/usr/bin/env python3

# from sqlalchemy import Column, Integer, DateTime, String
# from models.db import Base
from . import db, BaseMixin


class RfData(db.Model, BaseMixin):
    __tablename__ = 'rf_data'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    decimal = db.Column(db.Integer)
    bits = db.Column(db.Integer)
    binary = db.Column(db.String)
    pulse_length = db.Column(db.Integer)
    protocol = db.Column(db.Integer)

    def to_dict(self):
        return {
            'date': self.date,
            'decimal': self.decimal,
            'bits': self.bits,
            'binary': self.binary,
            'pulse_length': self.pulse_length,
            'protocol': self.protocol,
        }

    def to_ajax(self):
        return {
            'edit': '',
            'delete': '',
            'id': self.id,
            'date': self.date,
            'decimal': self.decimal if self.decimal else '-',
            'bits': self.bits if self.bits else '-',
            'binary': self.binary if self.binary else '-',
            'pulse_length': self.pulse_length if self.pulse_length else '-',
            'protocol': self.protocol if self.protocol else '-',
        }

    def __repr__(self):
        return (
            "<RfData("
            f"id={self.id}, "
            f"date={self.date}, "
            f"decimal={self.decimal}, "
            f"bits='{self.bits}', "
            f"binary='{self.binary}', "
            f"pulse_length={self.pulse_length}, "
            f"protocol={self.protocol})>"
        )
