import os
import requests
import pandas as pd
import sqlite3
from bs4 import BeautifulSoup
from contextlib import closing
import csv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://opensky-network.org/datasets/metadata/"
DB_FILENAME = "aircraftData.db"
TABLE_NAME = "aircraft_type"
LOG_FILENAME = "download_log.txt"
BOEING_747_CSV = "boeing_747_icao.csv"

def get_latest_csv_version(base_url):
    logger.info("Fetching the latest dataset version...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            files = [a['href'] for a in soup.find_all('a', href=True) if 'aircraft-database-complete' in a['href'] and a['href'].endswith('.csv')]
            if files:
                latest_file = sorted(files)[-1]
                logger.info(f"Found latest version: {latest_file}")
                return latest_file
            else:
                logger.warning("No CSV files found on the page.")
                return None
        else:
            logger.error("Failed to retrieve data from OpenSky Network.")
            return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

def download_csv(url, filename):
    logger.info(f"Downloading {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        logger.info("Download completed.")
        return True
    except Exception as e:
        logger.error(f"Failed to download the file: {e}")
        return False

def csv_to_sqlite(csv_file, db_file):
    logger.info(f"Converting the entire CSV {csv_file} to SQLite with table {TABLE_NAME}...")
    try:
        df = pd.read_csv(csv_file, low_memory=False, on_bad_lines='skip', quotechar="'", escapechar='\\')
        
        # Remove quotes from column names
        df.columns = df.columns.str.replace("'", "")
        
        with closing(sqlite3.connect(db_file)) as conn:
            df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        logger.info(f"SQLite database updated with {TABLE_NAME} data.")
        return True
    except Exception as e:
        logger.error(f"An error occurred while converting CSV to SQLite: {e}")
        return False

def get_column_names(db_file):
    logger.info("Getting column names from the database...")
    try:
        with closing(sqlite3.connect(db_file)) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
            columns = [row[1] for row in cursor.fetchall()]
            logger.info(f"Column names: {columns}")
            return columns
    except Exception as e:
        logger.error(f"An error occurred while getting column names: {e}")
        return []

def print_sample(db_file, columns):
    logger.info("Printing a sample of the database contents...")
    try:
        with closing(sqlite3.connect(db_file)) as conn:
            sample_query = f"""
            SELECT {', '.join(columns[:6])}  
            FROM {TABLE_NAME} 
            LIMIT 20
            """
            df = pd.read_sql_query(sample_query, conn)
            logger.info("Sample of database contents:")
            logger.info(df.to_string())
    except Exception as e:
        logger.error(f"An error occurred while printing sample data: {e}")

def filter_boeing_747(db_file, columns):
    logger.info("Filtering for Boeing 747 aircraft...")
    try:
        with closing(sqlite3.connect(db_file)) as conn:
            # Check total number of records
            total_count = pd.read_sql_query(f"SELECT COUNT(*) FROM {TABLE_NAME}", conn).iloc[0, 0]
            logger.info(f"Total records in database: {total_count}")

            # Determine which columns to use for filtering
            manufacturer_col = next((col for col in columns if 'manufacturer' in col.lower()), None)
            model_col = next((col for col in columns if 'model' in col.lower()), None)
            type_col = next((col for col in columns if 'type' in col.lower()), None)

            if not all([manufacturer_col, model_col, type_col]):
                logger.error("Could not find necessary columns for filtering")
                return False

            # Check for any Boeing aircraft
            boeing_query = f"""
            SELECT COUNT(*) FROM {TABLE_NAME} 
            WHERE LOWER({manufacturer_col}) LIKE '%boeing%' 
               OR LOWER({model_col}) LIKE '%boeing%'
               OR LOWER({type_col}) LIKE 'b7%'
            """
            boeing_count = pd.read_sql_query(boeing_query, conn).iloc[0, 0]
            logger.info(f"Total Boeing aircraft: {boeing_count}")

            # Check for 747 in any field
            query_747 = f"""
            SELECT COUNT(*) FROM {TABLE_NAME} 
            WHERE LOWER({model_col}) LIKE '%747%' 
               OR LOWER({type_col}) LIKE '%747%' 
               OR LOWER({type_col}) LIKE 'b74%'
            """
            count_747 = pd.read_sql_query(query_747, conn).iloc[0, 0]
            logger.info(f"Total aircraft with '747' in any field: {count_747}")

            # Updated query to be more inclusive
            icao24_col = next((col for col in columns if 'icao24' in col.lower()), None)
            registration_col = next((col for col in columns if 'registration' in col.lower()), None)

            query = f"""
            SELECT {icao24_col}, {registration_col}, {manufacturer_col}, {model_col}, {type_col}
            FROM {TABLE_NAME} 
            WHERE LOWER({model_col}) LIKE '%747%' 
               OR LOWER({type_col}) LIKE '%747%' 
               OR LOWER({type_col}) LIKE 'b74%'
               OR (LOWER({manufacturer_col}) LIKE '%boeing%' AND LOWER({model_col}) LIKE '%747%')
            """
            df = pd.read_sql_query(query, conn)
        
        if df.empty:
            logger.warning("No Boeing 747 aircraft found in the database.")
            return False

        df.to_csv(BOEING_747_CSV, index=False)
        logger.info(f"Boeing 747 aircraft data saved to {BOEING_747_CSV}")
        logger.info(f"Number of Boeing 747 aircraft: {len(df)}")
        logger.info("Sample of found aircraft:")
        logger.info(df.head().to_string())
        return True
    except Exception as e:
        logger.error(f"An error occurred while filtering Boeing 747 data: {e}")
        return False

def check_csv_structure(csv_file):
    logger.info(f"Checking structure of CSV file: {csv_file}")
    try:
        df = pd.read_csv(csv_file, nrows=5, quotechar="'", escapechar='\\')
        logger.info("First few rows of CSV:")
        logger.info(df.to_string())
        return True
    except Exception as e:
        logger.error(f"An error occurred while checking CSV structure: {e}")
        return False

def ensure_database_updated(csv_file, db_file):
    logger.info(f"Ensuring database {db_file} is up to date...")
    return csv_to_sqlite(csv_file, db_file)

def main():
    latest_version = get_latest_csv_version(BASE_URL)
    if latest_version:
        latest_csv_url = BASE_URL + latest_version
        latest_csv_filename = latest_version.split('/')[-1]

        if not os.path.exists(latest_csv_filename):
            if not download_csv(latest_csv_url, latest_csv_filename):
                logger.error("Failed to download the latest version.")
                return

        if check_csv_structure(latest_csv_filename):
            if ensure_database_updated(latest_csv_filename, DB_FILENAME):
                columns = get_column_names(DB_FILENAME)
                if columns:
                    print_sample(DB_FILENAME, columns)
                    if filter_boeing_747(DB_FILENAME, columns):
                        logger.info("Boeing 747 CSV file created/updated.")
                    else:
                        logger.error("Failed to create/update Boeing 747 CSV file.")
                else:
                    logger.error("Failed to get column names from the database.")
            else:
                logger.error("Failed to ensure database is updated.")
        else:
            logger.error("CSV file structure is not as expected.")

        # Cleanup
        if os.path.exists(latest_csv_filename):
            os.remove(latest_csv_filename)
            logger.info("Cleanup complete.")

        # Update log file
        with open(LOG_FILENAME, 'w') as log_file:
            log_file.write(latest_csv_filename)
    else:
        logger.error("Failed to identify latest version.")

if __name__ == "__main__":
    main()