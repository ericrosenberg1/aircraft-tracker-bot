# main.py

import schedule
import time
from opensky_api import fetch_aircraft_flights
from social_media_handler import post_updates
from storage import check_duplicate, update_record, store_estimated_landing
from config import AIRCRAFT_TYPE
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_flight(flight):
    flight_id = flight[0]  # ICAO24 code
    callsign = flight[1]
    origin_country = flight[2]
    longitude = flight[5]
    latitude = flight[6]
    altitude = flight[7]
    on_ground = flight[8]
    velocity = flight[9]

    flight_data = {
        'icao24': flight_id,
        'callsign': callsign,
        'origin_country': origin_country,
        'longitude': longitude,
        'latitude': latitude,
        'altitude': altitude,
        'on_ground': on_ground,
        'velocity': velocity
    }

    if not on_ground and not check_duplicate(flight_id):
        # This is likely a takeoff event
        estimated_landing_time = estimate_landing_time(flight_data)  # You'll need to implement this function
        message = f"A {AIRCRAFT_TYPE} (callsign: {callsign}) just took off from {origin_country}. " \
                  f"Current position: Lat {latitude}, Lon {longitude}, Alt {altitude}m, Speed {velocity}m/s. " \
                  f"Estimated landing time: {estimated_landing_time}"
        post_updates(flight_data, message)
        update_record(flight_data)
        store_estimated_landing(flight_id, estimated_landing_time)

def job():
    try:
        flights = fetch_aircraft_flights()
        for flight in flights:
            process_flight(flight)
    except Exception as e:
        logging.error(f"An error occurred during the scheduled job: {e}")

# Schedule to run every 5 minutes
schedule.every(5).minutes.do(job)

if __name__ == "__main__":
    logging.info("Starting 747 Flight Tracker Bot")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute if there's a job to run