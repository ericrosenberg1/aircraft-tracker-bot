import requests
import pandas as pd
from config import OPENSKY_API_USER, OPENSKY_API_PASS

def fetch_aircraft_flights():
    try:
        print("Loading ICAO24 codes from the CSV file...")
        icao_df = pd.read_csv('icao.csv')
        icao24_set = set(icao_df['icao24'].dropna())
        print(f"Loaded {len(icao24_set)} ICAO24 codes.")

        print("Fetching flights from OpenSky API...")
        url = 'https://opensky-network.org/api/states/all'
        response = requests.get(url, auth=(OPENSKY_API_USER, OPENSKY_API_PASS))
        response.raise_for_status()  # Ensure we got a valid response
        data = response.json()['states']
        print(f"Fetched {len(data)} flights.")

        print("Filtering flights for the specified aircraft types...")
        aircraft_flights = [flight for flight in data if flight[0] in icao24_set]
        print(f"Filtered {len(aircraft_flights)} flights for the specified aircraft types.")

        return aircraft_flights
    except Exception as e:
        print(f"An error occurred fetching aircraft flights: {e}")
        return []  # Return an empty list on error
