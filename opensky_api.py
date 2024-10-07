import requests
import pandas as pd
import os
from config import OPENSKY_API_USER, OPENSKY_API_PASS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOEING_747_CSV = "boeing_747_icao.csv"

def fetch_aircraft_flights():
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, BOEING_747_CSV)
        
        logger.info(f"Loading ICAO24 codes for Boeing 747 from {csv_path}...")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"The file {csv_path} does not exist. Please run update_aircraft_db.py first.")
        
        icao_df = pd.read_csv(csv_path)
        if icao_df.empty:
            logger.warning(f"The file {csv_path} is empty. No ICAO24 codes loaded.")
            return []
        
        icao24_set = set(icao_df['icao24'].dropna())
        if not icao24_set:
            logger.warning("No valid ICAO24 codes found in the CSV file.")
            return []
        
        logger.info(f"Loaded {len(icao24_set)} ICAO24 codes for Boeing 747.")

        logger.info("Fetching flights from OpenSky API...")
        url = 'https://opensky-network.org/api/states/all'
        response = requests.get(url, auth=(OPENSKY_API_USER, OPENSKY_API_PASS))
        response.raise_for_status()  # Ensure we got a valid response
        data = response.json()['states']
        logger.info(f"Fetched {len(data)} flights.")

        logger.info("Filtering flights for Boeing 747...")
        aircraft_flights = [flight for flight in data if flight[0] in icao24_set]
        logger.info(f"Filtered {len(aircraft_flights)} Boeing 747 flights.")

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