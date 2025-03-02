CREATE TABLE IF NOT EXISTS dives (
    path TEXT PRIMARY KEY,
    date TEXT,
    invalid_image NUMERIC,
    multiple_date NUMERIC,
    checksum TEXT);