#!/usr/bin/env python3

from datetime import datetime, timedelta

from ...models import db
from ...models.RoomData import RoomData
from ...models.State import State
from ...models.Tablet import TabletBattery
from ...models.Shopping import Liste


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
    if device == 'esp_bme_rf' and is_data_in_roomdata_table():
        data = get_latest_roomdata()
        if data['date'] > datetime.now() - timedelta(minutes=2):
            state = State(device=device, state="online", date=data['date'])
        else:
            state = State(device=device, state="offline", date=data['date'])
    elif device == "computer":
        state = State.query.filter_by(device=device).order_by(State.id.desc()).first()
        if state.date < datetime.now() - timedelta(minutes=16):
            state.state = "offline"
    elif device == "voice_assistant":
        state = State.query.filter_by(device=device).order_by(State.id.desc()).first()
        if state.date < datetime.now() - timedelta(minutes=16):
            state.state = "offline"
    else:
        state = State.query.filter_by(device=device).order_by(State.id.desc()).first()
    return state


def get_latest_tablet_data():
    # TODO incorperate charging state
    battery = TabletBattery.query.order_by(TabletBattery.id.desc()).first()
    if battery:
        if datetime.now() < battery.date + timedelta(minutes=30):
            return "online", battery.level, battery.date
        return "offline", battery.level, battery.date
    return "?", -99, None


def get_shopping_info(now, first_day, last_month, last_6_months, current_user):
    sum_this_month_query = db.session.query(Liste.price).filter_by(
        user=current_user
    ).filter(Liste.date.between(first_day, now))
    sum_this_month = sum([price[0] for price in sum_this_month_query])

    sum_last_month_query = db.session.query(Liste.price).filter_by(
        user=current_user
    ).filter(Liste.date.between(last_month, first_day))
    sum_last_month = sum([price[0] for price in sum_last_month_query])

    lists_last_6_months = Liste.query.filter_by(user=current_user).filter(Liste.date.between(last_6_months, first_day))
    return sum_this_month, sum_last_month, lists_last_6_months


def get_this_months_categories(current_user):
    """ Get bought items in the current month, sort by their categories and
        summarize the respective categories sums
    """
    now = datetime.now()
    first_of_month = datetime(year=now.year, month=now.month, day=1)
    listen = Liste.query.filter_by(user=current_user).filter(Liste.date.between(first_of_month, now))

    categories = {}
    for lisste in listen:
        for item in lisste.items:
            if item.category and item.category.name in categories.keys():
                # category already in, just add price
                categories[item.category.name] += item.price
            elif item.category:
                categories.update({item.category.name: item.price})
            else:
                if 'unknown' in categories.keys():
                    categories['unknown'] += item.price
                else:
                    categories.update({'unknown': item.price})
    return categories
