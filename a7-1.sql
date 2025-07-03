.open sqlite.db
DROP TABLE IF EXISTS events;

CREATE TABLE events(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT,
    date text,
    place text
);