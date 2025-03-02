UPDATE dives
SET date = :date,
    invalid_image = :invalid_iamge,
    multiple_date = :multiple_date
WHERE dives.path = :path;