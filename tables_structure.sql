CREATE TABLE IF NOT EXISTS instances
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song TEXT NOT NULL,
    artist TEXT NOT NULL,
    date_time TEXT NOT NULL,
    unix_time INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS songs
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    artist_2 TEXT,
    artist_3 TEXT,
    album TEXT,
    duration INTEGER,
    explicit TEXT,

);

CREATE TABLE IF NOT EXISTS artists
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    genres TEXT,
    type TEXT
);