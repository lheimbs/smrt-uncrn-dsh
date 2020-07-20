#!/usr/bin/env python3

import pandas as pd

from ...models.RoomData import RoomData


def is_data_in_roomdata_table():
    if RoomData.query.count():
        return True
    return False


def get_data_between(start_date, end_date):
    return RoomData.query.filter(RoomData.date.between(start_date, end_date)).order_by(RoomData.date)


def get_data_dict(data_query, nth_row):
    return pd.DataFrame([room_data.to_dict() for room_data in data_query.filter(RoomData.id % nth_row == 0)])
