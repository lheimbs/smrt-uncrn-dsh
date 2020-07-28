import os
from smrtuncrndsh import CSS_VARIABLES

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 60000)
COLORS = {**{
    'foreground': '#7FDBFF',  # 4491ed',
    'foreground-dark': '#123456',
    'background': '#111111',
    'background-medium': '#252525',
    'background-sub-medium': '#1c1c1c',
    'border-light': '#d6d6d6',
    'border-medium': '#333333',
    'border-dark': '#0f0f0f',
    'dark-1': '#222222',
    'dark-2': '#333333',
    'red': 'red',
    'green': 'green',
    'error': '#960c0c',
    'success': '#17960c',
    'warning': '#f7b731',
    'colorway': [
        '#fc5c65',
        '#26de81',
        '#fd9644',
        '#2bcbba',
        '#a55eea',
        '#bff739',
        '#45aaf2',
        '#fed330',
        '#4b7bec',
        '#778ca3',
        '#eb3b5a',
        '#2d98da',
        '#fa8231',
        '#3867d6',
        '#f7b731',
        '#8854d0',
        '#20bf6b',
        '#a5b1c2',
        '#0fb9b1',
        '#4b6584',
    ]
}, **CSS_VARIABLES}
UNITS = {
    'temperature': '°C',
    'pressure': 'hPa',
    'humidity': '%',
    'altitude': 'm',
    'brightness': 'lx',
}
