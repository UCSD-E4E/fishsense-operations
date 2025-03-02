INSERT INTO canonical_dives (path, date, invalid_image, multiple_date, checksum)
SELECT min(path), date, invalid_image, multiple_date, checksum FROM dives GROUP BY checksum
ON CONFLICT DO NOTHING;