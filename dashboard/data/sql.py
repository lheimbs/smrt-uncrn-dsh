#!/usr/bin/env python3

import logging

from ..app import db
from models.RoomData import RoomData

logger = logging.getLogger()


def is_data_in_roomdata_table():
    if RoomData.query.count():
        return True
    return False


def get_latest_roomdata():
    return RoomData.query.filter(
        RoomData.id == db.session.query(db.func.max(RoomData.id)).scalar()
    ).scalar().to_dict()


def get_min_temperature_roomdata():
    return db.session.query(db.func.min(RoomData.temperature)).scalar()


def get_max_temperature_roomdata():
    return db.session.query(db.func.max(RoomData.temperature)).scalar()


def get_min_humidity_roomdata():
    return db.session.query(db.func.min(RoomData.humidity)).scalar()


def get_max_humidity_roomdata():
    return db.session.query(db.func.max(RoomData.humidity)).scalar()


def get_min_pressure_roomdata():
    return db.session.query(db.func.min(RoomData.pressure)).scalar()


def get_max_pressure_roomdata():
    return db.session.query(db.func.max(RoomData.pressure)).scalar()


def get_last_24_hrs(start, end):
    data_query = db.session.query(
        RoomData.date, RoomData.temperature
    ).filter(
        RoomData.date.between(start, end)
    ).filter(
        RoomData.id % 2 == 0
    )
    return data_query
