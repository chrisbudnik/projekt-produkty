import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))


from unittest.mock import patch, MagicMock
from weather_data import get_weather_forecast, get_weather, get_location_and_timezone
import pandas as pd

mock_api_response = {
    "hourly": {
        "time": pd.date_range(start="2025-06-17", periods=200, freq="h")
        .strftime("%Y-%m-%dT%H:%M")
        .tolist(),
        "temperature_2m": [20] * 200,
        "relative_humidity_2m": [50] * 200,
        "wind_speed_10m": [10] * 200,
        "precipitation": [0] * 200,
        "rain": [0] * 200,
        "snowfall": [0] * 200,
        "weathercode": [1] * 200,
    },
    "current": {"time": "2025-06-17T00:00"},
}


@patch("weather_data.requests.get")
def test_get_weather_forecast(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_api_response

    df = get_weather_forecast(latitude=52.0, longitude=21.0, days=2, interval_hours=12)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 4  # 2 dni * 2 pomiary dziennie
    assert "temperature [°C]" in df.columns
    assert "storm" in df.columns


@patch("weather_data.requests.get")
def test_get_weather(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_api_response

    df = get_weather(latitude=52.0, longitude=21.0)
    assert isinstance(df, pd.DataFrame)
    assert len(df) <= 120
    assert "opis pogody [PL]" in df.columns


@patch("weather_data.Nominatim.geocode")
@patch("weather_data.TimezoneFinder.timezone_at")
def test_get_location_and_timezone(mock_timezone, mock_geocode):
    mock_geocode.return_value = MagicMock(
        latitude=52.2297, longitude=21.0122, address="Warszawa, Polska"
    )
    mock_timezone.return_value = "Europe/Warsaw"

    result = get_location_and_timezone(city="Warszawa", country="Polska")
    assert result["location"] == "Warszawa, Polska"
    assert result["timezone"] == "Europe/Warsaw"
    assert result["latitude"] == 52.2297
    assert result["longitude"] == 21.0122
