import sqlite3
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    conn = sqlite3.connect('flights.db')
    return conn

def check_duplicate(flight_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM flights WHERE id = ? AND status = 'in_progress'", (flight_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def update_record(flight):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO flights (id, callsign, takeoff_time, origin_country, status)
            VALUES (?, ?, datetime('now'), ?, 'in_progress')
        """, (flight['icao24'], flight['callsign'], flight['origin_country']))
        conn.commit()
        logger.info(f"Updated record for flight {flight['icao24']}")
    except sqlite3.Error as e:
        logger.error(f"Error updating record for flight {flight['icao24']}: {e}")
        conn.rollback()
    finally:
        conn.close()

def store_estimated_landing(flight_id, estimated_landing_time):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("""
            UPDATE flights
            SET estimated_landing_time = ?
            WHERE id = ? AND status = 'in_progress'
        """, (estimated_landing_time, flight_id))
        conn.commit()
        logger.info(f"Stored estimated landing time for flight {flight_id}")
    except sqlite3.Error as e:
        logger.error(f"Error storing estimated landing time for flight {flight_id}: {e}")
        conn.rollback()
    finally:
        conn.close()

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE IF NOT EXISTS flights
                     (id TEXT, callsign TEXT, takeoff_time TEXT, landing_time TEXT,
                      origin_country TEXT, estimated_landing_time TEXT, status TEXT)''')
        conn.commit()
        logger.info("Initialized flights database")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

# Call this function when your application starts
init_db()