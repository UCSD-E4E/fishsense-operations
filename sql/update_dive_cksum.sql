UPDATE dives
SET checksum = :checksum
WHERE dives.path = :path;