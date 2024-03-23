import schedule
import time
from opensky_api import fetch_aircraft_flights
from social_media_handler import post_updates
from storage import check_duplicate, update_record

def job():
    try:
        flights = fetch_aircraft_flights()
        for flight in flights:
            if not check_duplicate(flight['icao24']):
                post_updates(flight)
                update_record(flight)
    except Exception as e:
        print(f"An error occurred during the scheduled job: {e}")

# Schedule to run every 10 minutes, adjust as needed.
schedule.every(10).minutes.do(job)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)  # Adjust the sleep time as necessary
