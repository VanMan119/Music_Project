import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('spotify_tracker.db')
c = conn.cursor()

# Create instances table
c.execute("""
CREATE TABLE IF NOT EXISTS instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song TEXT NOT NULL,
    artist TEXT NOT NULL,
    date_time TEXT NOT NULL,
    unix_time INTEGER NOT NULL
)
""")

# Create songs table
c.execute("""
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    artist_2 TEXT,
    artist_3 TEXT,
    album TEXT,
    duration INTEGER,
    explicit BOOL
)
""")

# Create artists table
c.execute("""
CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    genres TEXT
)
""")

# Commit changes to save table creation
conn.commit()

# Creating our song class
class SongInstance:
    def __init__(self,name,date_time,unix_time,duration,album,popularity,explicit,artist,artist_2,artist_3, artist_genre):
        self.name = name
        self.date_time = date_time
        self.unix_time = unix_time
        self.duration = duration
        self.album = album
        self.popularity = popularity
        self.artist = artist
        self.artist_2 = artist_2
        self.artist_3 = artist_3
        self.explicit = explicit
        self.artist_genre = artist_genre

# Connection to spotify app
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="852f6556503043e9be0c04666cb9ce0f",
    client_secret="fd16afb6a5194fd0954059e79705d3a5",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-recently-played"
))

# Requesting JSON
results = sp.current_user_recently_played(limit=50)

# List to hold SongInstance objects
instances = []

# Getting list of artists to check against later
c.execute('SELECT name FROM artists')
rows = c.fetchall()
current_artists = []
for row in rows:
    current_artists.append(row[0])

# Getting data from recent tracks and converting them to SongInstance objects
for item in results['items']:
    track = item['track']
    name = track['name']
    date_time = item['played_at'][:10]+' '+item['played_at'][11:19]
    date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    unix_time = date_time.timestamp()
    duration = track['duration_ms']
    album = track['album']['name']
    popularity = track['popularity']
    explicit = track['explicit']
    artist = track['artists'][0]['name']
    try:
        artist_2 = track['artists'][1]['name']
    except IndexError:
        artist_2 = None
    try:
        artist_3 = track['artists'][2]['name']
    except IndexError:
        artist_3 = None

    # This bit is for time. Getting the genres takes a while so we only want to do it if 
    # we actually need to add a new artist. So we check if the artist is already in the
    # db, if it is, then add a blank genre
    artists_recorded = False
    for current_artist in current_artists:
        if artist == current_artist:
            artist_recorded = True
    if artists_recorded:
        artist_genres = ''
    else:
        artist_genres = ", ".join(sp.artist(track['artists'][0]['id']).get('genres', []))

    song_instance = SongInstance(name, date_time, unix_time, duration, album, popularity, explicit, artist, artist_2, artist_3, artist_genres)
    instances.append(song_instance)

# Getting current stored instances
# This is to avoid double counting instances
c.execute('SELECT song, artist, unix_time FROM instances')
rows = c.fetchall()
for row in rows:

    # Creating a SongInstance object for comparison
    row_song = row[0]
    row_artist = row[1]
    row_unix_time = row[2]
    for instance in instances:
        if (instance.name == row_song and instance.artist == row_artist and instance.unix_time == row_unix_time):
            instances.remove(instance)

for instance in instances:
    c.execute('INSERT INTO instances (song, artist, date_time, unix_time) VALUES (?, ?, ?, ?)', (instance.name, instance.artist, instance.date_time, instance.unix_time))

for instance in instances:

    # Get all songs from the database
    # Have to do this within the for loop to ensure it updates for any new additions
    c.execute('SELECT title, artist FROM songs')
    rows = c.fetchall()

    already_stored = False

    for row in rows:

        # Checking if both title and artist are the same
        if instance.name == row[0] and instance.artist == row[1]:
            already_stored = True
    if not already_stored:

        # Adding new songs to db
        c.execute('INSERT INTO songs (title, artist, album, duration, explicit, artist_2, artist_3) VALUES (?, ?, ?, ?, ?, ?, ?)', (instance.name, instance.artist, instance.album, instance.duration, instance.explicit, instance.artist_2, instance.artist_3))
        print(f"New song added: {instance.name} by {instance.artist}")

for instance in instances:

    # Get all artists from the database
    # Have to do this within the for loop to ensure it updates for any new additions
    c.execute('SELECT name FROM artists')
    rows = c.fetchall()

    already_stored = False

    for row in rows:
        # Checking if artist is the same
        if instance.artist == row[0]:
            already_stored = True
    if not already_stored:


        # Adding new artists to db
        c.execute('INSERT INTO artists (name, genres) VALUES (?, ?)', (instance.artist, instance.artist_genre))
        print(f"New artist added: {instance.artist}")

# Commit changes and close connection
conn.commit()
conn.close()