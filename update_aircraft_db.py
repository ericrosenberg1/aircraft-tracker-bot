import os
import requests
import pandas as pd
import sqlite3
from bs4 import BeautifulSoup
from contextlib import closing
import logging
import csv

# Constants
BASE_URL = "https://opensky-network.org/datasets/metadata/"
DB_FILENAME = "boeing747_data.db"
TABLE_NAME = "boeing747_aircraft"
LOG_FILENAME = "download_log.txt"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_latest_csv_version(base_url):
    logging.info("Fetching the latest dataset version...")
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        files = [a['href'] for a in soup.find_all('a', href=True) if 'aircraft-database-complete' in a['href'] and a['href'].endswith('.csv')]
        if files:
            latest_file = sorted(files)[-1]
            logging.info(f"Found latest version: {latest_file}")
            return latest_file
        else:
            logging.warning("No CSV files found on the page.")
            return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

def download_csv(url, filename):
    logging.info(f"Downloading {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        logging.info("Download completed.")
        return True
    except Exception as e:
        logging.error(f"Failed to download the file: {e}")
        return False

def csv_to_sqlite(csv_file, db_file):
    logging.info(f"Converting the CSV {csv_file} to SQLite and filtering for Boeing 747 aircraft...")
    try:
        # Read CSV with flexible parsing
        df = pd.read_csv(csv_file, encoding='ISO-8859-1', low_memory=False, 
                         on_bad_lines='skip', quoting=csv.QUOTE_ALL, 
                         skipinitialspace=True)
        
        # Log the number of rows and columns
        logging.info(f"CSV file loaded. Shape: {df.shape}")
        logging.info(f"Columns: {df.columns.tolist()}")
        
        # Try to find a column that might contain the model information
        model_column = next((col for col in df.columns if 'model' in col.lower()), None)
        if not model_column:
            logging.warning("Could not find a column containing model information.")
            return False
        
        # Filter for Boeing 747 aircraft
        boeing_747_df = df[df[model_column].str.contains('747', case=False, na=False)]
        
        logging.info(f"Filtered for Boeing 747 aircraft. Shape: {boeing_747_df.shape}")
        
        # Connect to SQLite database
        with closing(sqlite3.connect(db_file)) as conn:
            # Replace the entire table with new data
            boeing_747_df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        
        logging.info(f"SQLite database updated with Boeing 747 aircraft data. Total aircraft: {len(boeing_747_df)}")
        return True
    except Exception as e:
        logging.error(f"An error occurred while converting CSV to SQLite: {e}")
        return False

def main():
    latest_version = get_latest_csv_version(BASE_URL)
    if latest_version:
        latest_csv_url = BASE_URL + latest_version
        latest_csv_filename = latest_version.split('/')[-1]

        if os.path.exists(LOG_FILENAME):
            with open(LOG_FILENAME, 'r') as log_file:
                last_downloaded = log_file.readline().strip()
                if last_downloaded == latest_csv_filename:
                    logging.info("Latest version already downloaded. Skipping...")
                    return

        if download_csv(latest_csv_url, latest_csv_filename):
            if csv_to_sqlite(latest_csv_filename, DB_FILENAME):
                with open(LOG_FILENAME, 'w') as log_file:
                    log_file.write(latest_csv_filename)
                if os.path.exists(latest_csv_filename):
                    os.remove(latest_csv_filename)
                logging.info("Cleanup complete.")
            else:
                logging.error("Failed to process the CSV file.")
        else:
            logging.error("Failed to download the latest version.")
    else:
        logging.warning("No new version available or failed to identify latest version.")

if __name__ == "__main__":
    main()