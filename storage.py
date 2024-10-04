# storage.py

import sqlite3
import logging

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
    c.execute("""
        INSERT INTO flights (id, callsign, takeoff_time, origin_country, status)
        VALUES (?, ?, datetime('now'), ?, 'in_progress')
    """, (flight['icao24'], flight['callsign'], flight['origin_country']))
    conn.commit()
    conn.close()
    logging.info(f"Updated record for flight {flight['icao24']}")

def store_estimated_landing(flight_id, estimated_landing_time):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE flights
        SET estimated_landing_time = ?
        WHERE id = ? AND status = 'in_progress'
    """, (estimated_landing_time, flight_id))
    conn.commit()
    conn.close()
    logging.info(f"Stored estimated landing time for flight {flight_id}")

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS flights
                 (id TEXT, callsign TEXT, takeoff_time TEXT, landing_time TEXT,
                  origin_country TEXT, estimated_landing_time TEXT, status TEXT)''')
    conn.commit()
    conn.close()
    logging.info("Initialized flights database")

# Call this function when your application starts
init_db()