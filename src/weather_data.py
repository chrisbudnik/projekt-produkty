import requests
import pandas as pd
from datetime import datetime

def get_weather_dataframe(latitude, longitude):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,rain,snowfall"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,rain,snowfall"
        "&timezone=Europe%2FWarsaw"
    )
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Dane aktualne
        current = data.get("current", {})
        current_time = current.get("time")
        df_current = pd.DataFrame([{
            "time": current_time,
            "temperature [°C]": current.get("temperature_2m"),
            "humidity [%]": current.get("relative_humidity_2m"),
            "wind speed [km/h]": current.get("wind_speed_10m"),
            "precipitation [mm]": current.get("precipitation"),
            "rain [mm]": current.get("rain"),
            "snowfall [cm]": current.get("snowfall")
        }])

        # Dane godzinowe
        hourly = data.get("hourly", {})
        df_hourly = pd.DataFrame(hourly)

        # Tylko najbliższe 24 godziny od teraz
        df_hourly["time"] = pd.to_datetime(df_hourly["time"])
        df_next_24h = df_hourly[df_hourly["time"] > pd.to_datetime(current_time)].head(24)

        # Zmiana nazw kolumn
        df_next_24h = df_next_24h.rename(columns={
            "temperature_2m": "temperature [°C]",
            "relative_humidity_2m": "humidity [%]",
            "wind_speed_10m": "wind speed [km/h]",
            "precipitation": "precipitation [mm]",
            "rain": "rain [mm]",
            "snowfall": "snowfall [cm]"
        })

        # Połączenie obu
        df_result = pd.concat([df_current, df_next_24h], ignore_index=True)
        return df_result

    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

# Przykład użycia
df_weather = get_weather_dataframe(51.5074, -0.1278)  # Londyn
print(df_weather)
