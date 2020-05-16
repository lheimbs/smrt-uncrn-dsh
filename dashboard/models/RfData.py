#!/usr/bin/env python3

from sqlalchemy import Column, Integer, DateTime, String
from models.db import Base

class RfData(Base):
    __tablename__ = 'rf-data'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    decimal = Column(Integer)
    bits = Column(Integer)
    binary = Column(String)
    pulse_length = Column(Integer)
    protocol = Column(Integer)

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
