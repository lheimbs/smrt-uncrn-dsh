from datetime import datetime
from math import ceil, floor
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
import scipy.signal as signal
import plotly.graph_objects as go
import dash_html_components as html
from flask import current_app
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate

from .import sql
from ..variables import COLORS
from .weather import get_weather


def is_daytime(sunrise, sunset, now=None):
    if not now:
        now = datetime.now()
        if current_app.config['DEBUG']:
            now = datetime(year=now.year, month=now.month, day=now.day, hour=22)

    if sunrise < now < sunset:
        return True
    return False


def create_devices_callback(device):
    def device_callback(n, className):
        state = sql.get_latest_state(device)

        if not sql.is_data_in_state_table() or not state:
            className = className.replace("gone", "").replace("off", "").replace("on", "")
            className += " gone"
        else:
            if state and state.state in ['online', 'on']:
                className = className.replace("gone", "").replace("off", "").replace("on", "")
                className += " on"
            else:
                className = className.replace("gone", "").replace("off", "").replace("on", "")
                className += " off"

        return state.state if state else "?", className
    return device_callback


def init_callbacks(app):                    # noqa: C901
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside_2',
            function_name='make_radial_indicator'
        ),
        Output('temperature-display', 'children'),
        [
            Input('temperature-display', 'id'),
            Input('temperature_store', 'data')
        ]
    )

    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside_2',
            function_name='make_radial_indicator'
        ),
        Output('humidity-display', 'children'),
        [
            Input('humidity-display', 'id'),
            Input('humidity_store', 'data')
        ]
    )

    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside_2',
            function_name='make_radial_indicator'
        ),
        Output('pressure-display', 'children'),
        [
            Input('pressure-display', 'id'),
            Input('pressure_store', 'data')
        ]
    )

    @app.callback(
        Output('altitude-display', 'children'),
        [Input('last_entry', 'data')]
    )
    def get_altitude(data):
        if data:
            current_app.logger.debug(f"Updating altitude display ({round(data['altitude'], 2)} m).")
            return f"{round(data['altitude'], 2)} m"
        return ''

    @app.callback(
        Output('brightness-display', 'children'),
        [Input('last_entry', 'data')]
    )
    def get_brightness(data):
        if data:
            current_app.logger.debug(f"Updating brightness display ({round(data['brightness'], 2)} lx).")
            return f"{round(data['brightness'], 2)} lx"
        return ''

    @app.callback(
        Output('last_entry', 'data'),
        [Input('data-overview-update', 'n_intervals')]
    )
    def update_last_value(n):
        if not sql.is_data_in_roomdata_table():
            current_app.logger.warning("RoomData table has no entries. Cant fetch latest data.")
            last = None
        else:
            last = sql.get_latest_roomdata()
            current_app.logger.debug(f"Updating last values store ({last}).")
        return last

    @app.callback(
        Output('temperature_store', 'data'),
        [Input('last_entry', 'data')],
        [State('temperature_store', 'data')]
    )
    def update_temperature_store(latest_data, old_data):
        if latest_data:
            last = latest_data['temperature']
            current_app.logger.debug(f"Updating temperature store ({round(last, 2)}).")
            if (old_data and old_data['display'] == 0) or not old_data:
                old_data = {
                    'display': 1,
                    'new': last,
                    'old': 0,
                    'min': floor(sql.get_min_temperature_roomdata()),
                    'max': ceil(sql.get_max_temperature_roomdata()),
                }
            else:
                if last > old_data['max']:
                    old_data['max'] = last
                elif last < old_data['min']:
                    old_data['min'] = last

                old_data['old'] = old_data['new']
                old_data['new'] = last
        else:
            old_data = {
                'new': 0,
                'old': 0,
                'min': 0,
                'max': 0,
                'display': 0
            }
        # print(old_data)
        return old_data

    @app.callback(
        Output('pressure_store', 'data'),
        [Input('last_entry', 'data')],
        [State('pressure_store', 'data')]
    )
    def update_pressure_store(latest_data, old_data):
        if latest_data:
            last = latest_data['pressure']
            current_app.logger.debug(f"Updating pressure store ({round(last, 2)}).")
            if (old_data and old_data['display'] == 0) or not old_data:
                old_data = {
                    'display': 1,
                    'new': last,
                    'old': 0,
                    'min': floor(sql.get_min_pressure_roomdata()),
                    'max': ceil(sql.get_max_pressure_roomdata()),
                }
            else:
                if last > old_data['max']:
                    old_data['max'] = last
                elif last < old_data['min']:
                    old_data['min'] = last

                old_data['old'] = old_data['new']
                old_data['new'] = last
        else:
            old_data = {
                'new': 0,
                'old': 0,
                'min': 0,
                'max': 0,
                'display': 0
            }
        return old_data

    @app.callback(
        Output('humidity_store', 'data'),
        [Input('last_entry', 'data')],
        [State('humidity_store', 'data')]
    )
    def update_humidity_store(latest_data, old_data):
        if latest_data:
            last = latest_data['humidity']
            current_app.logger.debug(f"Updating humidity store ({round(last, 2)}).")
            if (old_data and old_data['display'] == 0) or not old_data:
                old_data = {
                    'display': 1,
                    'new': last,
                    'old': 0,
                    'min': floor(sql.get_min_humidity_roomdata()),
                    'max': ceil(sql.get_max_humidity_roomdata()),
                }
            else:
                if last > old_data['max']:
                    old_data['max'] = last
                elif last < old_data['min']:
                    old_data['min'] = last

                old_data['old'] = old_data['new']
                old_data['new'] = last
        else:
            old_data = {
                'new': 0,
                'old': 0,
                'min': 0,
                'max': 0,
                'display': 0
            }
        return old_data

    @app.callback(
        Output('day-data-graph', 'figure'),
        [Input('data-overview-update', 'n_intervals')],
    )
    def update_day_graph(interval):
        fig = go.Figure()

        fig.update_layout({
            'autosize': True,
            'coloraxis': {
                'colorbar': {
                    'outlinewidth': 0,
                    'bordercolor': COLORS['background'],
                    'bgcolor': COLORS['background'],
                },
            },
            'colorway': COLORS['colorway'],
            'font': {
                'family': "Ubuntu",
                'color': COLORS['font-foreground'],
            },
            'legend': {
                'orientation': 'h',
            },
            'margin': {
                'l': 10, 'r': 10, 't': 20, 'b': 10, 'pad': 0,
            },
            'paper_bgcolor': COLORS['transparent'],
            'plot_bgcolor': COLORS['transparent'],
            'xaxis': {
                'gridcolor': COLORS['dark-2'],
                'fixedrange': True,
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            },
            'yaxis': {
                'gridcolor': COLORS['dark-2'],
                'fixedrange': True,
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            }
        })

        if not sql.is_data_in_roomdata_table():
            current_app.logger.warning("RoomData table has no entries. Can't get last 24 hours data.")
            return fig
        else:
            current_app.logger.debug("Updating last 24 hours temperature graph.")

        now = datetime.now()
        start = now - relativedelta(days=1)

        data_query = sql.get_last_24_hrs(start, now)
        if data_query.count():
            day_data = pd.DataFrame([{'date': value[0], 'temperature': value[1]} for value in data_query])

            if day_data['temperature'].count() > 10:
                # Design of Buterworth filter
                filter_order = 2    # Filter order
                cutoff_freq = 0.2   # Cutoff frequency
                B, A = signal.butter(filter_order, cutoff_freq, output='ba')

                # Apply filter
                tempf = signal.filtfilt(B, A, day_data['temperature'])
            else:
                tempf = day_data['temperature']

            fig.add_trace(go.Scatter(
                x=day_data['date'],
                y=tempf,
                mode='lines',
                name='temperature',
                line={'color': COLORS['foreground']},
                hovertemplate="%{x|%d.%m.%Y %X} : %{y:.2f}°C<extra></extra>",
            ))
        return fig

    devices = ['computer', 'voice_assistant', 'esp_bme_rf', 'smrt-uncrn-cllctr', ]
    for device in devices:
        dynamically_generated_function = create_devices_callback(device)
        app.callback(
            [
                Output(f'{device}-status', 'children'),
                Output(f'{device}-status-container', 'className'),
            ],
            [Input('data-overview-update', 'n_intervals')],
            [State(f'{device}-status-container', 'className')]
        )(dynamically_generated_function)

    @app.callback(
        [
            Output('tablet-status', 'children'),
            Output('tablet-level', 'children'),
            Output('tablet-status-container', 'className'),
        ],
        [Input('data-overview-update', 'n_intervals')],
        [State('tablet-status-container', 'className')]
    )
    def device_callback(n, className):
        state, level = sql.get_latest_tablet_data()

        if not sql.is_data_in_tablet_table() or state == "?":
            className = className.replace("gone", "").replace("off", "").replace("on", "")
            className += " gone"
        else:
            if state in ['online', 'on']:
                className = className.replace("gone", "").replace("off", "").replace("on", "")
                className += " on"
            else:
                className = className.replace("gone", "").replace("off", "").replace("on", "")
                className += " off"

        return state, level, className

    @app.callback(
        Output('weather', 'data'),
        [Input('data-overview-update', 'n_intervals')],
    )
    def store_weather(n):
        # only update weather all 15 minutes TODO: updaterate in user-settings
        if n % 15 == 0:
            error, result = get_weather("Nürnberg")
            return {'error': error, 'result': result}
        raise PreventUpdate

    @app.callback(
        Output('weather-container', 'className'),
        [Input('weather', 'data')],
        [State('weather-container', 'className')]
    )
    def update_weather_background_color(data, classname):
        classname = classname.replace('day', '').replace('night', '')
        sunrise = datetime.fromtimestamp(data['result']['current']['sunrise_time'])
        sunset = datetime.fromtimestamp(data['result']['current']['sunset_time'])
        if is_daytime(sunrise, sunset):
            return classname + ' day'
        return classname + ' night'

    @app.callback(
        [
            Output('weather-current-date', 'children'),
            Output('weather-current-location', 'children'),
            Output('weather-current-icon', 'className'),
            Output('weather-current-temp', 'children'),
            Output('weather-current-feel', 'children'),
            Output('weather-current-wind', 'children'),
            Output('weather-current-wind-icon', 'style'),
            Output('weather-current-pressure', 'children'),
            Output('weather-current-humidity', 'children'),
            Output('weather-current-visibility', 'children'),
            Output('weather-current-dew', 'children'),
            Output('weather-current-uv', 'children'),
        ],
        [Input('weather', 'data')],
    )
    def update_current_weather(data):
        date = datetime.fromtimestamp(data['result']['current']['reference_time']).strftime("%a, %d.%m.%Y %H:%M:%S")
        icon = data['result']['current']['weather_code']
        temp = data['result']['current']['temperature']['temp']
        feels_like = data['result']['current']['temperature']['feels_like']
        detail = data['result']['current']['detailed_status']
        wind_speed = data['result']['current']['wind']['speed']
        wind_rotation = data['result']['current']['wind']['deg']
        return (
            date,
            "Nürnberg",
            f"owf owf-{icon} owf-2x",
            f"{temp:.1f} °C",  # TODO: unit in user settings
            f"Feels like {feels_like:.1f}°C.  {detail}.",  # TODO: unit in user settings
            f"{wind_speed} m/s",  # TODO: unit in user settings
            {
                'display': 'inline-block',
                'transform': f"rotate({wind_rotation+180}deg)",
                'padding': '0 0 10px 0'
            },
            f"Pressure: {data['result']['current']['pressure']['press']} hPa",
            f"Humidity: {data['result']['current']['humidity']} %",
            f"Visibility: {data['result']['current']['visibility_distance']} m",
            f"Dew point: {data['result']['current']['dewpoint']:.1f}°C",
            f"UV: {data['result']['current']['uvi']*100} %",
        )

    @app.callback(
        Output('weather-hours-graph', 'figure'),
        [Input('weather', 'data')],
    )
    def update_hours_weather(data):
        data = data['result']
        fig = go.Figure()

        if not data:
            current_app.logger.warning("No hourly weather data available.")
            return fig
        else:
            current_app.logger.debug("Updating hourly weather data.")

        hourly_data = pd.DataFrame(data['hours'][:6])
        hourly_data['feels_like'] = hourly_data.apply(lambda row: row.temperature['feels_like'], axis=1)
        hourly_data['temperature'] = hourly_data.apply(lambda row: row.temperature['temp'], axis=1)
        hourly_data['wind'] = hourly_data.apply(lambda row: row.wind['speed'], axis=1)
        hourly_data['pressure'] = hourly_data.apply(lambda row: row.pressure['press'], axis=1)
        hourly_data['rain'] = hourly_data.apply(lambda row: row.rain['1h'] if row.rain else 0, axis=1)
        hourly_data['snow'] = hourly_data.apply(lambda row: row.snow['1h'] if row.snow else 0, axis=1)
        hourly_data['reference_time'] = hourly_data.apply(
            lambda row: datetime.fromtimestamp(row.reference_time),
            axis=1
        )

        sunrise = datetime.fromtimestamp(data['current']['sunrise_time'])
        sunset = datetime.fromtimestamp(data['current']['sunset_time'])
        if is_daytime(sunrise, sunset):
            # day
            foreground_color = COLORS['background-card']
            graph_color = COLORS['foreground-dark']
        else:
            foreground_color = COLORS['font-foreground']
            graph_color = COLORS['foreground']

        fig.update_layout({
            'autosize': True,
            'barmode': 'overlay',
            'font': {
                'family': "Ubuntu",
            },
            'showlegend': False,
            'margin': {
                'l': 5, 'r': 5, 't': 10, 'b': 5, 'pad': 0,
            },
            'paper_bgcolor': COLORS['transparent'],
            'plot_bgcolor': COLORS['transparent'],
            'xaxis': {
                'color': foreground_color,
                'fixedrange': True,
                'showline': False, 'showgrid': False,
                'tickformat': "%H:00\n%a",
            },
            'yaxis': {
                'visible': False,
                'fixedrange': True,
                'overlaying': 'y2',
                'range': [hourly_data.temperature.min() - 0.5, hourly_data.temperature.max() + 0.5],
            },
            'yaxis2': {
                'fixedrange': True,
                'showline': False, 'linewidth': 1,
                'showgrid': False, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': foreground_color,
                'color': foreground_color,
                'side': 'right',
                'rangemode': 'tozero',
                'ticksuffix': "mm",
            }
        })

        fig.add_trace(go.Scatter(
            x=hourly_data['reference_time'],
            y=hourly_data['temperature'],
            mode='lines+text',
            name='temperature',
            line={'color': graph_color, 'smoothing': 1.3},
            fill="tozeroy",
            fillcolor=COLORS['orange_transparent'],
            textfont_color=foreground_color,
            textposition="top center",
            texttemplate="%{y:.1f}°C",
            customdata=np.stack((
                hourly_data.feels_like,
                hourly_data.wind,
                hourly_data.rain,
                hourly_data.snow,
                hourly_data.status,
                hourly_data.detailed_status,
            ), axis=-1),
            hovertemplate=(
                "%{x|%d.%m.%Y %X}<br>"
                "Temperature: %{y:.1f} °C<br>"
                "Feels like: %{customdata[0]:.1f} °C<br>"
                "Wind: %{customdata[1]:.1f} m/s<br>"
                "Regen: %{customdata[2]:.2f} mm<br>"
                "Schnee: %{customdata[3]:.2f} mm<br>"
                "%{customdata[4]}: %{customdata[5]}<br>"
                "<extra></extra>"
            ),
        ))
        fig.add_trace(go.Bar(
            x=hourly_data['reference_time'],
            y=hourly_data['rain'],
            marker={'color': COLORS['colorway'][8]},
            name='rain',
            # hovertemplate="%{x|%d.%m.%Y %X} : %{y:.2f}mm<extra></extra>",
            yaxis='y2',
            opacity=0.5,
            hoverinfo='skip',
            width=1000000,
        ))
        return fig

    @app.callback(
        Output('weather-days-container', 'children'),
        [Input('weather', 'data')],
    )
    def update_days_weather(data):
        if not data['result']:
            current_app.logger.debug(data['error'])
            return [html.P(data['error'])]

        data = data['result']
        children = []
        for day in data['days']:
            sunrise = datetime.fromtimestamp(day['sunrise_time']).strftime("%H:%M:%S")
            sunset = datetime.fromtimestamp(day['sunset_time']).strftime("%H:%M:%S")
            children.append(
                html.Div([
                    html.P(
                        datetime.fromtimestamp(day['reference_time']).strftime('%d.%m')
                    ),
                    html.I(className=f"owf owf-{day['weather_code']} owf-2x"),
                    html.H6(f"{day['temperature']['day']:.1f}°C"),
                    html.Span(
                        [
                            html.P(f"Sunrise: {sunrise}, Sunset: {sunset}"),
                            html.P(f"{day['detailed_status']}"),
                            html.P("Temperature:"),
                            html.P(f"min: {day['temperature']['min']:.1f}°C, max: {day['temperature']['max']:.1f}°C"),
                            html.P(f"Morning: {day['temperature']['morn']:.1f}°C, "),
                            html.P(f"Evening: {day['temperature']['eve']:.1f}°C, "),
                            html.P(f"Night: {day['temperature']['night']:.1f}°C"),
                        ],
                        className="tooltiptext large",
                    ),
                ], className="weather-daily-day tooltip")
            )
        return children
