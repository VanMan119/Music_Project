import sqlite3

# Connect to database
conn = sqlite3.connect('music_proj.db')
c = conn.cursor()

# Create instances table
c.execute("""
CREATE TABLE IF NOT EXISTS instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song TEXT NOT NULL,
    artist TEXT NOT NULL,
    time TEXT NOT NULL
)
""")

# Create songs table
c.execute("""
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT,
    duration INTEGER
)
""")

# Create artists table
c.execute("""
CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

# Commit changes to save table creation
conn.commit()

# Class to hold data for each song instance
class SongInstance:
    def __init__(self, song, artist, time):
        self.song = song
        self.artist = artist
        self.time = time

# List to hold SongInstance objects
instances = []

# Opening input text file and reading it
with open("input.txt", "r") as file:
    next(file)
    lines = file.readlines()

# Turning each line into a SongInstance object and appending it to instances list
for line in lines:
    line = line.strip()
    line = line.split("\t")
    song_instance = SongInstance(line[0], line[1], line[2])
    instances.append(song_instance)

# Getting current stored instances
# This is to avoid double counting instances
c.execute('SELECT song, artist, time FROM instances')
rows = c.fetchall()
for row in rows:

    # Creating a SongInstance object for comparison
    song_instance = SongInstance(row[0], row[1], row[2])
    for instance in instances:

        # If the song and time are the same, remove it from new instances list
        if instance.song == song_instance.song and instance.time == song_instance.time:
            instances.remove(instance)

# Inserting new instances into the database
for instance in instances:
    c.execute('INSERT INTO instances (song, artist, time) VALUES (?, ?, ?)', (instance.song, instance.artist, instance.time))

# Checking for new songs
for instance in instances:

    # Get all songs from the database
    # Have to do this within the for loop to ensure it updates for any new additions
    c.execute('SELECT title, artist FROM songs')
    rows = c.fetchall()

    already_stored = False

    for row in rows:

        # Checking if both title and artist are the same
        if instance.song == row[0] and instance.artist == row[1]:
            already_stored = True
    if not already_stored:

        # Adding new songs to db
        c.execute('INSERT INTO songs (title, artist) VALUES (?, ?)', (instance.song, instance.artist))
        print(f"New song added: {instance.song} by {instance.artist}")

# Checking for new artists
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
        c.execute('INSERT INTO artists (name) VALUES (?)', (instance.artist,))
        print(f"New artist added: {instance.artist}")

# Commit changes and close connection
conn.commit()
conn.close()

