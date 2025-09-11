import requests
import os
import csv
from config import OPENSKY_API_USER, OPENSKY_API_PASS, PASSENGER_TYPECODES
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOEING_747_CSV = "boeing_747_icao.csv"

def _load_passenger_747_icao24(csv_path):
    icao24_set = set()
    try:
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                icao = (row.get('icao24') or '').strip()
                typecode = (row.get('typecode') or '').strip().upper()
                # Passenger only: include if explicitly passenger type
                if icao and typecode and typecode in PASSENGER_TYPECODES:
                    icao24_set.add(icao)
    except Exception as e:
        logger.error(f"Failed reading {csv_path}: {e}")
        return set()
    return icao24_set


def fetch_aircraft_flights():
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, BOEING_747_CSV)
        
        logger.info(f"Loading ICAO24 codes for Boeing 747 from {csv_path}...")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"The file {csv_path} does not exist. Please run update_aircraft_db.py first.")
        
        icao24_set = _load_passenger_747_icao24(csv_path)
        if not icao24_set:
            logger.warning("No valid ICAO24 codes found in the CSV file.")
            return []
        
        logger.info(f"Loaded {len(icao24_set)} passenger Boeing 747 ICAO24 codes.")

        logger.info("Fetching flights from OpenSky API...")
        url = 'https://opensky-network.org/api/states/all'
        headers = {'Accept-Encoding': 'gzip, deflate', 'User-Agent': '747Tracker/1.0'}
        response = requests.get(url, headers=headers, auth=(OPENSKY_API_USER, OPENSKY_API_PASS), timeout=15)
        response.raise_for_status()  # Ensure we got a valid response
        data = response.json()['states']
        logger.info(f"Fetched {len(data)} flights.")

        logger.info("Filtering flights for Boeing 747...")
        aircraft_flights = [flight for flight in data if flight[0] in icao24_set]
        logger.info(f"Filtered {len(aircraft_flights)} passenger Boeing 747 flights.")

        return aircraft_flights
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from OpenSky API: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return []
