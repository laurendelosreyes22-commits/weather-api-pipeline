import os
import requests
import time
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

api_url = "https://api.weatherapi.com/v1/forecast.json" # API endpoint for 7-day forecast

zip_codes = [
    "90045",  # Los Angeles, CA
    "10001",  # New York, NY
    "60601",  # Chicago, IL
    "98101",  # Seattle, WA
    "33101",  # Miami, FL
    "77001",  # Houston, TX
    "85001",  # Phoenix, AZ
    "19101",  # Philadelphia, PA
    "78201",  # San Antonio, TX
    "92101",  # San Diego, CA
    "75201",  # Dallas, TX
    "95101",  # San Jose, CA
    "78701",  # Austin, TX
    "30301",  # Atlanta, GA
    "28201",  # Charlotte, NC
    "43201",  # Columbus, OH
    "80201",  # Denver, CO
    "32801",  # Orlando, FL
    "89101",  # Las Vegas, NV
    "37201",  # Nashville, TN
]

results = []

for zip_code in zip_codes:
    # Parameters for the API request
    params = {
        "key": API_KEY,
        "q": zip_code,
        "days": 7
    }

    response = requests.get(api_url, params=params)
    if not response.ok or not response.text:
        raise RuntimeError(f"API request failed for {zip_code}: HTTP {response.status_code} — {response.text!r}")
    data = response.json()

    city = data["location"]["name"]

    for day in data["forecast"]["forecastday"]:
        date = day["date"]
        max_temp = day["day"]["maxtemp_f"]
        min_temp = day["day"]["mintemp_f"]
        condition = day["day"]["condition"]["text"]

        results.append({
            "zip_code": zip_code,
            "city": city,
            "date": date,
            "max_temp_f": max_temp,
            "min_temp_f": min_temp,
            "condition": condition
        })

        print(f"{city} {date}: {max_temp}°F / {min_temp}°F, {condition}")

    time.sleep(1)  # 1-second delay to avoid rate limiting

df = pd.DataFrame(results)
print(df)
print(f"\nShape: {df.shape[0]} rows x {df.shape[1]} columns")

df.to_csv("weather_data.csv", index=False)
print("Saved to weather_data.csv")