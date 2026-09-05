import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")


# print("API Key:", repr(API_KEY))
# print("Length:", len(API_KEY) if API_KEY else "None")


def get_weather(city: str):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    response = requests.get(url, timeout=10)

    # print("URL:", url)
    # print("Status Code:", response.status_code)
    # print("Response:", response.text)

    if response.status_code != 200:
        return "Unable to fetch weather."

    data = response.json()

    return {
        "city": city,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
    }


def get_weather_forecast(city: str, days: int = 1):
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    response = requests.get(url, timeout=10)

    # print("URL:", url)
    # print("Status Code:", response.status_code)
    # print("Response:", response.text)

    if response.status_code != 200:
        return "Unable to fetch weather forecast."

    data = response.json()
    forecast_list = data.get("list", [])

    if not forecast_list:
        return "Unable to fetch weather forecast."

    target_date = (datetime.now() + timedelta(days=days)).date().strftime("%Y-%m-%d")
    matching_entries = [entry for entry in forecast_list if entry["dt_txt"].startswith(target_date)]

    if not matching_entries:
        return "No forecast available for the requested day."

    best_entry = min(matching_entries, key=lambda entry: abs(int(entry["dt_txt"][11:13]) - 12))

    return {
        "city": city,
        "date": target_date,
        "temperature": best_entry["main"]["temp"],
        "humidity": best_entry["main"]["humidity"],
        "condition": best_entry["weather"][0]["description"],
    }