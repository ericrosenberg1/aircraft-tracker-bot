import schedule
import time
from opensky_api import fetch_aircraft_flights
from social_media_handler import post_updates
from storage import check_duplicate, update_record, store_estimated_landing, init_db
from config import AIRCRAFT_TYPE
import logging
import os
from datetime import datetime, timedelta
import math
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load airport database
AIRPORT_DB = {}
try:
    with open('airport_db.json', 'r') as f:
        AIRPORT_DB = json.load(f)
except FileNotFoundError:
    logger.warning("Airport database not found. Please run update_airport_db.py first.")

def distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def get_airport_info(latitude, longitude):
    if not AIRPORT_DB:
        return ("UNK", "Unknown City", "Unknown Country")
    nearest_airport = min(AIRPORT_DB.items(), key=lambda x: distance(latitude, longitude, x[1]['lat'], x[1]['lon']))
    code = nearest_airport[0]
    info = nearest_airport[1]
    return (code, info['city'], info['country'])

def estimate_landing_time(flight_data):
    if 'destination' in flight_data and flight_data['destination'] in AIRPORT_DB:
        dest = AIRPORT_DB[flight_data['destination']]
        dist = distance(flight_data['latitude'], flight_data['longitude'], dest['lat'], dest['lon'])
        est_duration = dist / 800  # Assuming an average speed of 800 km/h
        return datetime.now() + timedelta(hours=est_duration)
    return None

def get_destination(flight_data):
    # This is a placeholder. In reality, you'd need to use a flight schedule API or database.
    callsign = flight_data['callsign'].strip()
    if len(callsign) > 3:
        possible_dest = callsign[-3:]
        if possible_dest in AIRPORT_DB:
            return possible_dest
    return None

def enrich_flight_data(flight_data):
    origin_airport, origin_city, origin_country = get_airport_info(flight_data['latitude'], flight_data['longitude'])
    flight_data['origin'] = origin_airport
    flight_data['origin_city'] = origin_city
    flight_data['origin_country'] = origin_country
    flight_data['destination'] = get_destination(flight_data)
    flight_data['estimated_landing_time'] = estimate_landing_time(flight_data)
    return flight_data

def process_flight(flight):
    try:
        flight_id, callsign, origin_country, last_contact, last_position_update, longitude, latitude, altitude, on_ground, velocity, *_ = flight

        flight_data = {
            'icao24': flight_id,
            'callsign': callsign,
            'origin_country': origin_country,
            'longitude': longitude,
            'latitude': latitude,
            'altitude': altitude,
            'on_ground': on_ground,
            'velocity': velocity,
            'last_contact': last_contact
        }

        if datetime.now() - datetime.fromtimestamp(last_contact) > timedelta(minutes=10):
            logger.debug(f"Skipped old flight {flight_id}")
            return

        if not on_ground and not check_duplicate(flight_id):
            enriched_data = enrich_flight_data(flight_data)
            
            message = f"A {AIRCRAFT_TYPE} (callsign: {callsign}) just took off from {enriched_data['origin']} Airport, {enriched_data['origin_city']}, {enriched_data['origin_country']}."
            
            if enriched_data['destination']:
                message += f" Destination: {enriched_data['destination']}."
            
            if enriched_data['estimated_landing_time']:
                message += f" Estimated landing time: {enriched_data['estimated_landing_time'].strftime('%Y-%m-%d %H:%M:%S UTC')}."

            try:
                post_updates(enriched_data, message)
            except Exception as e:
                logger.error(f"Error posting update for flight {flight_id}: {e}", exc_info=True)
            
            update_record(enriched_data)
            if enriched_data['estimated_landing_time']:
                store_estimated_landing(flight_id, enriched_data['estimated_landing_time'])
            logger.info(f"Processed takeoff event for flight {flight_id}")
        else:
            logger.debug(f"Skipped flight {flight_id} (on ground: {on_ground}, duplicate: {check_duplicate(flight_id)})")
    except Exception as e:
        logger.error(f"Error processing flight {flight}: {e}", exc_info=True)

def job():
    try:
        flights = fetch_aircraft_flights()
        if not flights:
            logger.warning("No flights fetched. The boeing_747_icao.csv file might be missing or empty.")
            return
        logger.info(f"Fetched {len(flights)} flights. Processing...")
        for flight in flights:
            process_flight(flight)
        logger.info("Finished processing all flights.")
    except Exception as e:
        logger.error(f"An error occurred during the scheduled job: {e}", exc_info=True)

def check_required_files():
    required_files = ['boeing_747_icao.csv', 'config.py', 'airport_db.json']
    missing_files = [file for file in required_files if not os.path.exists(file)]
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}. Please ensure all required files are present.")
        return False
    return True

def main():
    logger.info("Starting 747 Flight Tracker Bot")
    if not check_required_files():
        logger.error("Exiting due to missing required files.")
        return

    init_db()

    schedule.every(5).minutes.do(job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()