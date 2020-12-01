import logging
from datetime import datetime

from flask import current_app
from pyowm.owm import OWM
from pyowm.commons import exceptions as OSMExceptions

logging.getLogger("urllib3").setLevel(logging.WARNING)
owm = OWM(current_app.config['OWM_API_KEY'])


def get_weather(location):
    owm_mgr = owm.weather_manager()
    owm_regs = owm.city_id_registry()

    loc = owm_regs.locations_for(location)
    err, res = "", None
    if loc:
        try:
            res_obj = owm_mgr.one_call(lat=loc[0].lat, lon=loc[0].lon, units='metric')

            res = {
                'current': res_obj.current.to_dict(),
                'hours': [hourly.to_dict() for hourly in res_obj.forecast_hourly],
                'days': [daily.to_dict() for daily in res_obj.forecast_daily[0:6]],
            }
        except OSMExceptions.BadGatewayError:
            err = "OWM API backends suffers communication issues."
        except OSMExceptions.TimeoutError:
            err = "OWM API suffered timeout due to slow response times upstream."
        except OSMExceptions.InvalidSSLCertificateError:
            err = "It is impossible to verify the SSL certificates provided by the OWM APIs."
        except OSMExceptions.NotFoundError:
            err = "This resource is not available!"
        except OSMExceptions.UnauthorizedError:
            err = "The requested resource is not available with the given API key!"
        except OSMExceptions.ParseAPIResponseError:
            err = "It is to parse the JSON payload of API response!"
    else:
        err = f"Location '{location}' is invalid!"
    return err, res
