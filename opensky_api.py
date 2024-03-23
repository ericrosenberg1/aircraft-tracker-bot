import requests
import pandas as pd
from config import OPENSKY_API_USER, OPENSKY_API_PASS, AIRCRAFT_DB_PATH

# Load the aircraft database to filter for Boeing 747s
aircraft_df = pd.read_csv(AIRCRAFT_DB_PATH)
b747_df = aircraft_df[aircraft_df['Model'].str.contains('747', na=False)]
b747_icao24 = set(b747_df['icao24'].dropna())

def fetch_747_flights():
    try:
        url = 'https://opensky-network.org/api/states/all'
        response = requests.get(url, auth=(OPENSKY_API_USER, OPENSKY_API_PASS))
        response.raise_for_status()  # Ensure we got a valid response
        data = response.json()['states']
        b747_flights = [flight for flight in data if flight[0] in b747_icao24]
        return b747_flights
    except Exception as e:
        print(f"An error occurred fetching 747 flights: {e}")
        return []  # Return an empty list on error
