#!/usr/bin/env python3

from datetime import datetime, timedelta

from ...models import db
from ...models.RoomData import RoomData
from ...models.State import State
from ...models.Tablet import TabletBattery


def is_data_in_roomdata_table():
    if RoomData.query.first():
        return True
    return False


def is_data_in_state_table():
    if State.query.first():
        return True
    return False


def is_data_in_tablet_table():
    if TabletBattery.query.first():
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
    state = State.query.filter_by(device=device).order_by(State.id.desc()).first()
    if device == 'esp_bme_rf' and is_data_in_roomdata_table():
        data = get_latest_roomdata()
        if state.date > data['date']:
            return state
        else:
            return State(device=device, state="online", date=data['date'])
    return state


def get_latest_tablet_data():
    # TODO incorperate charging state
    battery = TabletBattery.query.order_by(TabletBattery.id.desc()).first()
    if battery:
        if datetime.now() < battery.date + timedelta(minutes=30):
            return "online", battery.level, battery.date
        return "offline", battery.level, battery.date
    return "?", -99, None
