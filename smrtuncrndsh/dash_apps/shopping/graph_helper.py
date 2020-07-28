#!/usr/bin/env python

from math import floor, pow

GRIDLINES = 4


def calculate_ticks(y1_min, y1_max, y2_min, y2_max):
    if y1_min < 0:
        y1_range = y1_max - y1_min
    else:
        y1_range = y1_max

    y1_range = y1_range * 1000
    y1_len = len(str(floor(y1_range)))

    y1_pow10_divisor = pow(10, y1_len - 1)
    y1_firstdigit = floor(y1_range / y1_pow10_divisor)
    y1_max_base = y1_pow10_divisor * y1_firstdigit / 1000

    y1_dtick = y1_max_base / GRIDLINES

    y1_pow10_divisor = pow(10, y1_len - 1) / 1000
    y1_range = y1_range / 1000

    if y2_min < 0:
        y2_range = y2_max - y2_min
    else:
        y2_range = y2_max

    y2_range = y2_range * 1000
    y2_len = len(str(floor(y2_range)))

    y2_pow10_divisor = pow(10, y2_len - 1)
    y2_firstdigit = floor(y2_range / y2_pow10_divisor)
    y2_max_base = y2_pow10_divisor * y2_firstdigit / 1000

    y2_dtick = y2_max_base / GRIDLINES

    y2_pow10_divisor = pow(10, y2_len - 1) / 1000
    y2_range = y2_range / 1000

    y1_dtick_ratio = y1_range / y1_dtick
    y2_dtick_ratio = y2_range / y2_dtick

    global_dtick_ratio = max(y1_dtick_ratio, y2_dtick_ratio)

    negative = False

    if y1_min < 0:
        negative = True
        y1_negative_ratio = abs(y1_min / y1_range) * global_dtick_ratio
    else:
        y1_negative_ratio = 0

    if y2_min < 0:
        negative = True
        y2_negative_ratio = abs(y2_min / y2_range) * global_dtick_ratio
    else:
        y2_negative_ratio = 0

    global_negative_ratio = max(y1_negative_ratio, y2_negative_ratio) + 0.1

    if negative:
        y1_range_min = (global_negative_ratio) * y1_dtick * -1
        y2_range_min = (global_negative_ratio) * y2_dtick * -1
    else:
        y1_range_min = 0
        y2_range_min = 0

    y1_positive_ratio = abs(y1_max / y1_range) * global_dtick_ratio
    y2_positive_ratio = abs(y2_max / y2_range) * global_dtick_ratio

    global_positive_ratio = max(y1_positive_ratio, y2_positive_ratio) + 0.1

    y1_range_max = (global_positive_ratio) * y1_dtick
    y2_range_max = (global_positive_ratio) * y2_dtick

    return y1_range_min, y1_range_max, y1_dtick, y2_range_min, y2_range_max, y2_dtick


def calculate_ticks_multi(ticks):
    for i, vals in ticks.items():
        y_min, y_max = vals['min'], vals['max']

        if y_min < 0:
            y_range = y_max - y_min
        else:
            y_range = y_max

        y_range = y_range * 1000
        y_len = len(str(floor(y_range)))

        y_pow10_divisor = pow(10, y_len - 1)
        y_firstdigit = floor(y_range / y_pow10_divisor)
        y_max_base = y_pow10_divisor * y_firstdigit / 1000

        y_dtick = y_max_base / GRIDLINES

        y_pow10_divisor = pow(10, y_len - 1) / 1000
        y_range = y_range / 1000

        y_dtick_ratio = y_range / y_dtick

        vals.update({
            'range': y_range,
            'dtick': y_dtick,
            'dtick_ratio': y_dtick_ratio,
        })

    global_dtick_ratio = max([tick['dtick_ratio'] for tick in ticks.values()])
    negative = False

    for i, vals in ticks.items():
        if vals['min'] < 0:
            negative = True
            y_negative_ratio = abs(vals['min'] / vals['range']) * global_dtick_ratio
        else:
            y_negative_ratio = 0
        vals.update({'negative_ratio': y_negative_ratio})

    global_negative_ratio = max([tick['negative_ratio'] for tick in ticks.values()]) + 0.1

    if negative:
        for i, vals in ticks.items():
            y_range_min = (global_negative_ratio) * vals['dtick'] * -1
            vals.update({'range_min': y_range_min})
    else:
        for i, vals in ticks.items():
            vals.update({'range_min': 0})

    for i, vals in ticks.items():
        y_positive_ratio = abs(vals['max'] / vals['range']) * global_dtick_ratio
        vals.update({'positive_ratio': y_positive_ratio})

    global_positive_ratio = max([tick['positive_ratio'] for tick in ticks.values()]) + 0.1

    for i, vals in ticks.items():
        y_range_max = global_positive_ratio * vals['dtick']
        vals.update({'range_max': y_range_max})

    return ticks
