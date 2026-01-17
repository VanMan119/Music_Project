import sqlite3
import json
from datetime import datetime, timedelta, timezone
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# ------ CLOUD CONNECTION ----------
DB_FILE_NAME = "spotify_tracker.db"

SERVICE_ACCOUNT_JSON_CONTENT = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON")


if SERVICE_ACCOUNT_JSON_CONTENT:
    # Running on GitHub: write secret to temp file
    with open("/tmp/service_account.json", "w") as f:
        f.write(SERVICE_ACCOUNT_JSON_CONTENT)
    service_json_path = "/tmp/service_account.json"
else:
    # Running locally: use local JSON file
    service_json_path = "/home/stonee5936/Projects/Test/spotify-tracker-project.json"


scope = ['https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    service_json_path, scopes=scope
)
gauth = GoogleAuth()
gauth.credentials = credentials
drive = GoogleDrive(gauth)

file_list = drive.ListFile({'q': f"title='{DB_FILE_NAME}' and trashed=false"}).GetList()
if file_list:
    file_list[0].GetContentFile(DB_FILE_NAME)
    print(f"File size after download: {os.path.getsize(DB_FILE_NAME)} bytes")

    print(f"Downloaded '{DB_FILE_NAME}' from Google Drive.")
else:
    print(f"No file named '{DB_FILE_NAME}' found on Google Drive. A new local DB will be created.")


now = datetime.now(timezone.utc)

last_week = now - timedelta(days=7)
last_week = int(last_week.timestamp())

month_start = now.replace(day=1)
month_start = int(month_start.timestamp())

year_start = now.replace(month=1, day=1)
year_start = int(year_start.timestamp())

# Connect to database
conn = sqlite3.connect(DB_FILE_NAME)
c = conn.cursor()

def query_artists(c, start_time):
    c.execute("""
          SELECT
          artists.name,
          SUM(songs.duration) / 60000.0 AS minutes,
          COUNT(*) AS plays
          FROM instances
          JOIN songs ON instances.song = songs.title AND instances.artist = songs.artist
          JOIN artists ON songs.artist = artists.name
          WHERE instances.unix_time >= ?
          GROUP BY artists.name
          ORDER BY minutes DESC
          """, (start_time,))

    rows = c.fetchall()

    artists = [
    {
        "name": row[0],
        "minutes": round(row[1],2),
        "plays": row[2]
    }
    for row in rows
    ]

    total_minutes = sum(a["minutes"] for a in artists) or 1

    for a in artists:
        a["percentageOfMinutes"] = round((a["minutes"]/total_minutes)*100,1)

    return artists

total_artists = query_artists(c, 0)
week_artists = query_artists(c, last_week)
month_artists = query_artists(c, month_start)
year_artists = query_artists(c, year_start)


def query_songs(c, start_time):
    c.execute("""
        SELECT songs.title, 
              artists.name, 
              SUM(songs.duration) / 60000.0 AS minutes,
              COUNT(*) as plays
        FROM instances
        JOIN songs ON instances.song = songs.title AND instances.artist = songs.artist
        JOIN artists ON songs.artist = artists.name
        WHERE instances.unix_time >= ?
        GROUP BY songs.title, artists.name
        ORDER BY minutes DESC
        """, (start_time,))
    
    rows = c.fetchall()

    songs = [
        {
            "title": row[0],
            "artist": row[1],
            "minutes": row[2],
            "plays": row[3]
        }
        for row in rows
    ]
    total_minutes = sum(s["minutes"] for s in songs) or 1

    for s in songs:
        s["percentageOfMinutes"] = round(
            (s["minutes"] / total_minutes) * 100, 1
        )
    
    return songs

total_songs = query_songs(c, 0)
week_songs = query_songs(c, last_week)
month_songs = query_songs(c, month_start)
year_songs = query_songs(c, year_start)

stats = {
    "meta": {
        "generatedAt": now.isoformat()
    },
    "artists": {
        "total": total_artists,
        "lastWeek": week_artists,
        "month": month_artists,
        "year": year_artists
    },
    "songs": {
        "total": total_songs,
        "lastWeek": week_songs,
        "month": month_songs,
        "year": year_songs
    }
}

with open("data.json", "w") as f:
    json.dump("data.json",f,indent=2)
    print("data dumped")