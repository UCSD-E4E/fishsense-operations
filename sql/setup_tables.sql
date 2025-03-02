CREATE TABLE IF NOT EXISTS dives (
    path TEXT PRIMARY KEY,
    date TEXT,
    invalid_image NUMERIC,
    multiple_date NUMERIC,
    checksum TEXT);
CREATE TABLE IF NOT EXISTS images (
    path TEXT PRIMARY KEY,
    dive TEXT REFERENCES dives (path),
    camera_sn TEXT
);
CREATE TABLE IF NOT EXISTS canonical_dives (
    path TEXT PRIMARY KEY,
    date TEXT,
    invalid_image NUMERIC,
    multiple_date NUMERIC,
    checksum TEXT
);