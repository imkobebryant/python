import sqlite3
import requests

# 下載 JSON 資料
url = "https://data.moenv.gov.tw/api/v2/aqx_p_432?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=ImportDate%20desc&format=JSON"
response = requests.get(url)
data = response.json()['records']

# 連接到 SQLite 資料庫
conn = sqlite3.connect('AQI.db')
cursor = conn.cursor()

# 創建資料表（如果尚未存在）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sitename TEXT,
        county TEXT,
        aqi INTEGER,
        status TEXT,
        pm25 NUMERIC,
        date TEXT,
        lat NUMERIC,
        lon NUMERIC,
        UNIQUE(date, sitename)
    )
''')

# 插入資料，使用 INSERT OR REPLACE 確保不重複
for record in data:
    cursor.execute('''
        INSERT OR REPLACE INTO records (sitename, county, aqi, status, pm25, date, lat, lon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        record['sitename'],
        record['county'],
        int(record['aqi']) if record['aqi'].isdigit() else None,
        record['status'],
        float(record['pm2.5']) if record['pm2.5'] else None,
        record['publishtime'],
        float(record['latitude']) if record['latitude'] else None,
        float(record['longitude']) if record['longitude'] else None
    ))

# 提交更改並關閉連接
conn.commit()
conn.close()