import requests
import sqlite3
import json
from datetime import datetime

DB_NAME = 'D:\python視窗設計\GitHub\python_視窗設計\lesson7\AQI.db'

def download_data():
    url = "https://data.moenv.gov.tw/api/v2/aqx_p_432?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=ImportDate%20desc&format=JSON"
    response = requests.get(url)
    data = response.json()
    return data['records']

def save_to_database(records):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sitename TEXT,
                        county TEXT,
                        aqi INTEGER,
                        status TEXT,
                        pm25 REAL,
                        date TEXT,
                        lat REAL,
                        lon REAL,
                        UNIQUE(sitename, date)
                    )''')
    
    for record in records:
        try:
            cursor.execute('''INSERT OR REPLACE INTO records (sitename, county, aqi, status, pm25, date, lat, lon)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (record['SiteName'], record['County'], int(record['AQI']), record['Status'], 
                            float(record['PM2.5']), record['ImportDate'], float(record['Latitude']), 
                            float(record['Longitude'])))
        except KeyError:
            continue
    
    conn.commit()
    conn.close()

def main():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM records")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        records = download_data()
        save_to_database(records)
    else:
        print("Database already populated with data.")

if __name__ == '__main__':
    main()
