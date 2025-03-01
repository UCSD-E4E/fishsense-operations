'''Discovery backend
'''
import datetime as dt
import multiprocessing
from pathlib import Path
from typing import Optional, Tuple
from hashlib import md5

import numpy as np
from PIL import ExifTags, Image

def get_image_date(path: Path) -> Optional[dt.datetime]:
    try:
        img = Image.open(path)
        exif = img.getexif()
        creation_time_str = exif.get(ExifTags.Base.DateTime)
        creation_time = dt.datetime.strptime(creation_time_str, '%Y:%m:%d %H:%M:%S')
        return creation_time
    except Exception:
        return None

def get_dive_date(path: Path) -> Tuple[dt.date, bool, bool]:
    jpgs = path.glob('*.jpg', case_sensitive=False)
    with multiprocessing.Pool() as pool:
        img_dates = pool.map(get_image_date, jpgs)
    invalid_dates = any(date is None for date in img_dates)
    valid_dates = [date for date in img_dates if date]
    timestamps = [date.timestamp() for date in valid_dates]
    if len(timestamps) == 0:
        return None, False, False
    end_time = dt.datetime.fromtimestamp(max(timestamps))
    start_time = dt.datetime.fromtimestamp(min(timestamps))
    multiple_dates = (end_time.date() != start_time.date())
    mean_date = dt.datetime.fromtimestamp(np.mean(timestamps)).date()
    return mean_date, invalid_dates, multiple_dates

def get_file_checksum(path: Path) -> str:
    cksum = md5()
    with open(path, 'rb') as handle:
        for blob in iter(lambda: handle.read(8192), b''):
            cksum.update(blob)
    return cksum.hexdigest()

def get_dive_checksum(path: Path) -> str:
    reference_data = sorted(path.rglob('*.orf', case_sensitive=False))
    with multiprocessing.Pool() as pool:
        checksums = pool.map(get_file_checksum, reference_data)
    cksum = md5()
    for idx, file in enumerate(reference_data):
        cksum.update(f'{file.name}:{checksums[idx]}\n'.encode())
    return cksum.hexdigest()
