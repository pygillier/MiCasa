from pathlib import Path
from dynamic_preferences.registries import global_preferences_registry
from weatherapi import WeatherPoint
import json


registry = global_preferences_registry.manager()


def get_weather():
    weather = {}

    try:
        point = WeatherPoint(
            lat=registry["weather__latitude"],
            lon=registry["weather__longitude"],
        )
        point.set_key(registry["weather__apikey"])
        point.get_current_weather()

        if registry["weather__temperature"] == "celsius":
            weather["temp"] = f"{point.temp_c}°C"
        else:
            weather["temp"] = f"{point.temp_f}°F"

        # Icon
        moment = "day" if point.is_day else "night"
        weather["icon"] = get_icon(point.condition_code, moment)

        # Extra coverage
        weather["extra"] = f"{getattr(point, registry['weather__coverage'], 0)}%"
    except:  # noqa
        weather = {"icon": "na", "temp": 0, "extra": "Unknown"}
    finally:
        return weather


def get_icon(code: int, moment: str) -> str:
    f = Path(__file__).parent.resolve() / "mappings.json"

    with f.open() as source:
        mappings = json.loads(source.read())
        chosen = [x for x in mappings if x["code"] == code]
        if len(chosen) == 1:
            return chosen[0]["icon"][moment]
        else:
            return "na"
