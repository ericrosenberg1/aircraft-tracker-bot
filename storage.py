import sqlite3

def get_db_connection():
    conn = sqlite3.connect('flights.db')
    return conn

def check_duplicate(flight_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM flights WHERE id = ?", (flight_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def update_record(flight):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO flights (id, takeoff_time, landing_time, status) VALUES (?, ?, ?, ?)",
              (flight['icao24'], flight.get('takeoff_time'), flight.get('landing_time'), 'completed'))
    conn.commit()
    conn.close()
