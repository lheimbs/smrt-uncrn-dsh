#!/usr/bin/env python3

from ...models import db
from ...models.RoomData import RoomData
from ...models.State import State


def is_data_in_roomdata_table():
    if RoomData.query.first():
        return True
    return False


def is_data_in_state_table():
    if State.query.first():
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
    ).order_by(RoomData.date)
    return data_query


def get_latest_state(device):
    return State.query.filter_by(device=device).order_by(State.id.desc()).first()
