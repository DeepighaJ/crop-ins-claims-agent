import requests
import csv
from datetime import datetime
from app.config import Config

def get_ndvi_comparison(location_id: str, event_date: str) -> dict:
    """Finds nearest NDVI readings before/after event_date and calculates the delta."""
    try:
        target_date = datetime.strptime(event_date, "%Y-%m-%d")
        readings = []
        
        with open(Config.NDVI_CSV_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID'] == location_id:
                    readings.append({
                        "date": datetime.strptime(row['Date'], "%Y-%m-%d"),
                        "ndvi": float(row['MOD13Q1_061__250m_16_days_NDVI'])
                    })
        
        if not readings:
            return {"error": f"No NDVI data found for location ID '{location_id}'."}

        readings.sort(key=lambda x: x["date"])
        before_readings = [r for r in readings if r["date"] < target_date]
        after_readings = [r for r in readings if r["date"] >= target_date]
        
        if not before_readings or not after_readings:
            return {"error": "Insufficient data to calculate delta around the event date."}
            
        before, after = before_readings[-1], after_readings[0]
        return {
            "before_date": before["date"].strftime("%Y-%m-%d"),
            "before_ndvi": before["ndvi"],
            "after_date": after["date"].strftime("%Y-%m-%d"),
            "after_ndvi": after["ndvi"],
            "delta": round(after["ndvi"] - before["ndvi"], 4)
        }
    except Exception as e:
        return {"error": f"Failed to process NDVI data: {str(e)}"}

def get_historical_weather(lat: float, lon: float, event_date: str) -> dict:
    """Fetches Open-Meteo historical daily data for the event_date."""
    try:
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": event_date,
            "end_date": event_date,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "timezone": "auto"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        daily = response.json().get("daily", {})
        
        return {
            "max_temp_c": daily.get("temperature_2m_max", [None])[0],
            "min_temp_c": daily.get("temperature_2m_min", [None])[0],
            "precip_sum_mm": daily.get("precipitation_sum", [None])[0],
            "max_wind_kmh": daily.get("wind_speed_10m_max", [None])[0]
        }
    except Exception as e:
        return {"error": f"Network or API failure fetching weather data: {str(e)}"}
