import sqlite3
import logging
import time
import hashlib

logger = logging.getLogger(__name__)

DB_PATH = 'flights.db'


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
        # Core flights table
        c.execute('''CREATE TABLE IF NOT EXISTS flights
                     (id TEXT, callsign TEXT, takeoff_time TEXT, landing_time TEXT,
                      origin_country TEXT, estimated_landing_time TEXT, status TEXT,
                      message_hash TEXT, last_posted_at TEXT)''')
        # Add missing columns for migrations
        existing_cols = {r[1] for r in c.execute("PRAGMA table_info(flights)")}
        if 'message_hash' not in existing_cols:
            c.execute("ALTER TABLE flights ADD COLUMN message_hash TEXT")
        if 'last_posted_at' not in existing_cols:
            c.execute("ALTER TABLE flights ADD COLUMN last_posted_at TEXT")

        # Indexes for performance
        c.execute("CREATE INDEX IF NOT EXISTS idx_flights_id_status ON flights(id, status)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_flights_takeoff ON flights(takeoff_time)")

        # Rate limit tracking
        c.execute('''CREATE TABLE IF NOT EXISTS rate_limits (
                        network TEXT,
                        window_start INTEGER,
                        count INTEGER,
                        PRIMARY KEY (network)
                    )''')

        # Message hash dedupe
        c.execute('''CREATE TABLE IF NOT EXISTS message_hashes (
                        hash TEXT PRIMARY KEY,
                        created_at TEXT
                    )''')
        conn.commit()
        logger.info("Initialized flights database")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

def _now_epoch() -> int:
    return int(time.time())


def can_post(network: str, window_seconds: int, max_posts: int) -> bool:
    conn = get_db_connection()
    c = conn.cursor()
    try:
        now = _now_epoch()
        row = c.execute("SELECT window_start, count FROM rate_limits WHERE network = ?", (network,)).fetchone()
        if not row:
            c.execute("INSERT INTO rate_limits(network, window_start, count) VALUES (?, ?, 0)", (network, now))
            conn.commit()
            return True
        window_start, count = row
        if now - window_start >= window_seconds:
            c.execute("UPDATE rate_limits SET window_start = ?, count = 0 WHERE network = ?", (now, network))
            conn.commit()
            return True
        return count < max_posts
    except sqlite3.Error as e:
        logger.error(f"Rate limit check failed: {e}")
        return True  # Fail-open to avoid blocking forever
    finally:
        conn.close()


def record_post(network: str):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        row = c.execute("SELECT window_start, count FROM rate_limits WHERE network = ?", (network,)).fetchone()
        if not row:
            c.execute("INSERT INTO rate_limits(network, window_start, count) VALUES (?, ?, 1)", (network, _now_epoch()))
        else:
            window_start, count = row
            c.execute("UPDATE rate_limits SET count = ? WHERE network = ?", (count + 1, network))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Rate limit record failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def make_message_hash(message: str) -> str:
    return hashlib.sha256(message.encode('utf-8')).hexdigest()


def is_duplicate_message(message_hash: str, window_seconds: int = 24 * 3600) -> bool:
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Check if the exact message hash exists within the window
        row = c.execute(
            "SELECT created_at FROM message_hashes WHERE hash = ?",
            (message_hash,)
        ).fetchone()
        if not row:
            return False
        # Keep it simple: any prior same hash counts as duplicate within window
        # Optional: could store epoch and compare here if needed
        return True
    except sqlite3.Error as e:
        logger.error(f"Message dedupe check failed: {e}")
        return False
    finally:
        conn.close()


def record_message_hash(message_hash: str):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT OR IGNORE INTO message_hashes(hash, created_at) VALUES (?, datetime('now'))",
            (message_hash,)
        )
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Message hash record failed: {e}")
        conn.rollback()
    finally:
        conn.close()


def cleanup_db(retention_days: int = 30, completion_grace_hours: int = 6, stale_in_progress_hours: int = 24):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Mark flights completed where ETA passed long ago
        c.execute(
            """
            UPDATE flights
            SET status = 'completed', landing_time = COALESCE(landing_time, estimated_landing_time)
            WHERE status = 'in_progress'
              AND estimated_landing_time IS NOT NULL
              AND datetime(estimated_landing_time) <= datetime('now', ?)
            """,
            (f'-{completion_grace_hours} hours',)
        )

        # Mark very old in-progress flights as completed (fallback)
        c.execute(
            """
            UPDATE flights
            SET status = 'completed'
            WHERE status = 'in_progress'
              AND takeoff_time IS NOT NULL
              AND datetime(takeoff_time) <= datetime('now', ?)
            """,
            (f'-{stale_in_progress_hours} hours',)
        )

        # Purge old completed flights
        c.execute(
            """
            DELETE FROM flights
            WHERE status = 'completed'
              AND landing_time IS NOT NULL
              AND datetime(landing_time) <= datetime('now', ?)
            """,
            (f'-{retention_days} days',)
        )

        # Purge old message hashes beyond retention
        c.execute(
            "DELETE FROM message_hashes WHERE datetime(created_at) <= datetime('now', ?)",
            (f'-{retention_days} days',)
        )

        conn.commit()
        # Vacuum to reclaim space
        c.execute("VACUUM")
        logger.info("Database cleanup completed")
    except sqlite3.Error as e:
        logger.error(f"Database cleanup failed: {e}")
        conn.rollback()
    finally:
        conn.close()
