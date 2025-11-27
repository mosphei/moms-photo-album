from PIL import Image
from datetime import datetime
import re
import os
from typing import Optional

# Regex pattern to match "yyyymmdd_hhmmss" somewhere in the filename
# It looks for 8 digits, an underscore, and 6 digits.
FILENAME_PATTERN = re.compile(r"(\d{8})_(\d{6})")

def get_date_from_filename(filename: str) -> Optional[datetime]:
    """
    Attempts to extract a datetime object from a filename following the 
    'yyyymmdd_hhmmss' convention.
    """
    match = FILENAME_PATTERN.search(filename)
    if match:
        date_str = match.group(1)  # e.g., "20240115"
        time_str = match.group(2)  # e.g., "103000"
        full_datetime_str = date_str + time_str
        
        try:
            # Parse the combined string: YYYYMMDDHHMMSS
            return datetime.strptime(full_datetime_str, '%Y%m%d%H%M%S')
        except ValueError:
            # In case the matched digits are not a valid date (e.g., 99999999)
            print(f"Matched pattern but failed to parse valid date/time: {full_datetime_str}")
            return None
    else:
        print(f"Filename '{filename}' does not follow the yyyymmdd_hhmmss convention.")
        return None


def get_image_date(img: Image, filename: str) -> Optional[datetime]:
    """
    Attempts to get the date from EXIF data first. 
    If not found, falls back to parsing the filename.
    """
    # 1. Try EXIF data
    try:
        exif_data = img.getexif()
        date_str = exif_data.get(36867) or exif_data.get(306) # DateTimeOriginal or DateTime
        if date_str:
            print(f"Date found in EXIF data: {date_str}")
            return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except (IOError, OSError, AttributeError, ValueError):
        # Catches file errors, no exif data errors, or bad EXIF string format errors
        print("EXIF data extraction failed or not present.")

    # 2. Fallback to Filename parsing if EXIF fails
    print("Falling back to filename parsing...")
    return get_date_from_filename(filename)

