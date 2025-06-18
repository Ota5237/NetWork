.open sqlite.db
.mode box
DROP TABLE IF EXISTS images;

CREATE TABLE images(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT,
    date TEXT,
    place TEXT,
    object TEXT
);