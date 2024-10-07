import requests
import json
import schedule
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
AIRPORT_DB_URL = "https://raw.githubusercontent.com/mwgg/Airports/master/airports.json"
LOCAL_DB_FILENAME = "airport_db.json"
LOG_FILENAME = "airport_db_update_log.txt"

def fetch_airport_data():
    logger.info("Fetching airport data...")
    try:
        response = requests.get(AIRPORT_DB_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching airport data: {e}")
        return None

def process_airport_data(data):
    logger.info("Processing airport data...")
    processed_data = {}
    for code, airport in data.items():
        processed_data[code] = {
            "name": airport.get("name", "Unknown"),
            "city": airport.get("city", "Unknown"),
            "country": airport.get("country", "Unknown"),
            "lat": airport.get("lat", 0),
            "lon": airport.get("lon", 0)
        }
    return processed_data

def save_airport_data(data):
    logger.info(f"Saving airport data to {LOCAL_DB_FILENAME}...")
    try:
        with open(LOCAL_DB_FILENAME, 'w') as f:
            json.dump(data, f)
        logger.info("Airport data saved successfully.")
        return True
    except IOError as e:
        logger.error(f"Error saving airport data: {e}")
        return False

def update_airport_db():
    logger.info("Starting airport database update...")
    
    data = fetch_airport_data()
    if data:
        processed_data = process_airport_data(data)
        if save_airport_data(processed_data):
            with open(LOG_FILENAME, 'w') as log_file:
                log_file.write(datetime.now().isoformat())
            logger.info("Airport database update completed successfully.")
        else:
            logger.error("Failed to save airport data.")
    else:
        logger.error("Failed to fetch airport data.")

def main():
    logger.info("Airport database updater started.")
    
    # Run the update immediately when the script starts
    update_airport_db()
    
    # Schedule the update to run monthly
    schedule.every(30).days.do(update_airport_db)

    try:
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Sleep for an hour between checks
    except KeyboardInterrupt:
        logger.info("Airport database updater stopped by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()