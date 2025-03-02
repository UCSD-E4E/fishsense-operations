INSERT INTO images (path, dive)
VALUES (:path, :dive)
ON CONFLICT DO NOTHING;