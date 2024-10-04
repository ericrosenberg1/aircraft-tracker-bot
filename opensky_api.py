# opensky_api.py

import requests
import pandas as pd
from config import OPENSKY_API_USER, OPENSKY_API_PASS, AIRCRAFT_TYPE
import logging

def fetch_aircraft_flights():
    try:
        logging.info(f"Loading ICAO24 codes for {AIRCRAFT_TYPE} from the CSV file...")
        icao_df = pd.read_csv('boeing_747_icao.csv')
        icao24_set = set(icao_df['icao24'].dropna())
        logging.info(f"Loaded {len(icao24_set)} ICAO24 codes for {AIRCRAFT_TYPE}.")

        logging.info("Fetching flights from OpenSky API...")
        url = 'https://opensky-network.org/api/states/aircraft'
        params = {'icao24': ','.join(icao24_set)}
        response = requests.get(url, auth=(OPENSKY_API_USER, OPENSKY_API_PASS), params=params)
        response.raise_for_status()  # Ensure we got a valid response
        data = response.json()['states']
        logging.info(f"Fetched {len(data)} {AIRCRAFT_TYPE} flights.")

        return data
    except Exception as e:
        logging.error(f"An error occurred fetching aircraft flights: {e}")
        return []  # Return an empty list on error