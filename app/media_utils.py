import hashlib
import mimetypes
from fastapi import HTTPException, status
import ffmpeg
import os
from datetime import datetime
import re
from PIL import Image, ImageFile
import imagehash

from app.models import PhotoModel
from app.settings import MEDIADIR

FILENAME_PATTERN = re.compile(r"(\d{8})_(\d{6})")


def get_date_from_filename(filename: str) -> datetime | None:
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
            return datetime.strptime(full_datetime_str, "%Y%m%d%H%M%S")
        except ValueError:
            # In case the matched digits are not a valid date (e.g., 99999999)
            print(
                f"Matched pattern but failed to parse valid date/time: {full_datetime_str}"
            )
            return None
    else:
        print(f"Filename '{filename}' does not follow the yyyymmdd_hhmmss convention.")
        return None


def get_image_date(img: ImageFile.ImageFile, filename: str) -> datetime | None:
    """
    Attempts to get the date from EXIF data first.
    If not found, falls back to parsing the filename.
    """
    # 1. Try EXIF data
    try:
        exif_data = img.getexif()
        date_str = exif_data.get(36867) or exif_data.get(
            306
        )  # DateTimeOriginal or DateTime
        if date_str:
            print(f"Date found in EXIF data: {date_str}")
            return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    except (IOError, OSError, AttributeError, ValueError):
        # Catches file errors, no exif data errors, or bad EXIF string format errors
        print("EXIF data extraction failed or not present.")

    # 2. Fallback to Filename parsing if EXIF fails
    print("Falling back to filename parsing...")
    return get_date_from_filename(filename)


def get_metadata_ffmpeg_python(video_path):
    """
    Retrieves video metadata using the ffmpeg-python probe function.
    """
    try:
        probe = ffmpeg.probe(video_path)
        return probe
    except ffmpeg.Error as e:
        print(f"FFmpeg Error: {e.stderr.decode()}")
        return None


def extract_creation_time(metadata) -> datetime | None:
    """
    Attempts to find the creation time within the metadata dictionary.
    """
    if not metadata:
        return None

    creation_time_str: str | None = None

    # 1. Check in the global format tags first (most common location)
    format_tags = metadata.get("format", {}).get("tags", {})
    creation_time_str = format_tags.get("creation_time")

    if creation_time_str:
        return datetime.fromisoformat(creation_time_str)

    # 2. If not found globally, check specific stream tags (e.g., the video stream)
    streams = metadata.get("streams", [])
    for stream in streams:
        if stream.get("codec_type") == "video":
            stream_tags = stream.get("tags", {})
            creation_time_str = stream_tags.get("creation_time")
            if creation_time_str:
                return datetime.fromisoformat(creation_time_str)
            break  # Found the video stream, no need to check others

    return None


def create_video_thumbnail(
    video_path: str, output_path: str, max_width: int, max_height: int
):
    """
    Generates a meaningful thumbnail using FFmpeg's thumbnail filter in Python.
    """
    try:
        (
            ffmpeg.input(video_path)
            # Apply the 'thumbnail' filter to find the best frame
            .filter("thumbnail")
            # Apply the 'scale' filter using a simple auto-adjusting strategy
            # For a max-width of 320 and max-height of 240, for example:
            .filter("scale", w=max_width, h=max_height)
            .output(
                output_path,
                vframes=1,
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(f"Meaningful thumbnail created at {output_path}")
    except ffmpeg.Error as e:
        print(f"FFmpeg Error: {e.stderr.decode()}")


def get_content_type_by_extension(filepath):
    """
    Determines content type based on the file extension.
    """
    # guess_type returns a tuple: (type, encoding)
    content_type, encoding = mimetypes.guess_type(filepath)

    if content_type:
        if content_type == 'model/vnd.mts':
            return 'video/MP2T'
        return content_type
    else:
        return "application/octet-stream"  # Default fallback for unknown types


def make_photo_from_file(user_id: int, relative_path: str) -> PhotoModel:
    md5_hash = hashlib.md5()
    filename = os.path.basename(relative_path)
    file_path = os.path.join(MEDIADIR, str(user_id), relative_path)
    size = os.path.getsize(file_path)
    content_type = get_content_type_by_extension(file_path)
    md5sum = None
    with open(file_path, "rb") as f:
        # Read the file in chunks (e.g., 8192 bytes)
        for chunk in iter(lambda: f.read(8192), b""):
            md5_hash.update(chunk)
        md5sum = md5_hash.hexdigest()

    # get the image hash
    img = None
    img_hash = None
    date_taken = datetime(1900, 1, 1, 0, 0, 0)
    try:
        if content_type.startswith("image/"):
            with Image.open(file_path) as img:
                img_hash = imagehash.average_hash(img)
                date_taken = get_image_date(img, str(file_path))
        elif content_type.startswith("video/"):
            "must be a video"
            metadata = get_metadata_ffmpeg_python(file_path)
            print(metadata)
            if metadata is not None:
                date_taken = extract_creation_time(metadata)
            if date_taken is None:
                # filename?
                date_taken = get_date_from_filename(str(file_path))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {content_type}. Only image files are allowed.",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

    photo = PhotoModel(
        user_id=user_id,
        file_path=relative_path,
        filename=filename,
        date_taken=date_taken,
        hash=img_hash,
        md5sum=md5sum,
        size=size,
        content_type=content_type,
    )
    return photo
