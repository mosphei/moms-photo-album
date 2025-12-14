from datetime import datetime
import hashlib
import os
import re
import shutil
import tempfile
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from PIL import Image, ImageFile
import imagehash
import textwrap
import ffmpeg

from ..settings import MEDIADIR
from ..security import get_current_user
from ..schemas import PhotoSchema
from ..models import PhotoModel, User
from ..database import get_db


router = APIRouter(
    prefix="/api/upload",  # Sets the base path for all routes in this file
    tags=["upload"],  # Groups these routes in the API docs (Swagger UI)
)

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


# Upload image endpoint
@router.post("/", response_model=PhotoSchema)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filename = str(file.filename)
    base_name, extension = os.path.splitext(filename)

    if file.content_type is None:
        content_type = "unknown"
    else:
        content_type = file.content_type

    if content_type.startswith("image/"):
        pass
    elif content_type.startswith("video/"):
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}. Only image files are allowed.",
        )
    # use a named temporary file in order to ffprobe
    md5_hash = hashlib.md5()
    temp_file_path = None
    md5sum = None
    size = 0
    # 1. Create a temporary file and stream content while hashing
    try:
        # Use tempfile.NamedTemporaryFile to get a physical path name
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f"_{file.filename}", mode="wb"
        ) as temp_file:
            # Read the UploadFile in chunks and update both the hash and the temp file
            while chunk := await file.read(8192):  # Read in chunks of 8192 bytes
                md5_hash.update(chunk)
                temp_file.write(chunk)

            temp_file_path = temp_file.name

        # Get the final MD5 hexdigest after the file is completely written
        md5sum = md5_hash.hexdigest()
        size = os.path.getsize(temp_file_path)
    finally:
        # Ensure the original upload stream is closed by FastAPI
        await file.close()

    # try and get exact matches
    dupe: PhotoModel | None = None
    dupe = (
        db.query(PhotoModel)
        .filter(and_(PhotoModel.size == size, PhotoModel.md5sum == md5sum))
        .first()
    )

    if not dupe is None:
        # this file has already been uploaded
        return dupe

    # get the image hash
    img = None
    img_hash = None
    date_taken = None
    try:
        if content_type == "image":
            with Image.open(temp_file_path) as img:
                img_hash = imagehash.average_hash(img)
                date_taken = get_image_date(img, filename)
        else:
            "must be a video"
            metadata = get_metadata_ffmpeg_python(temp_file_path)
            print(metadata)
            if metadata is not None:
                date_taken = extract_creation_time(metadata)
            if date_taken is None:
                # filename?
                date_taken = get_date_from_filename(filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

    if date_taken:
        parent_dirs = os.path.join(f"{date_taken.year:04d}", f"{date_taken.month:02d}")
    else:
        " split it on the filename to avoid directories with too many files"
        left_12 = base_name[:12]
        chunks_list = textwrap.wrap(left_12, 4)
        parent_dirs = os.path.join(*chunks_list)
        # set a date
        date_taken = datetime(1900, 1, 1, 0, 0, 0)

    upload_dir = os.path.join(MEDIADIR, str(current_user.id), parent_dirs)
    os.makedirs(upload_dir, exist_ok=True)
    file_location = os.path.join(upload_dir, filename)
    # does the file already exist?
    count = 0
    while os.path.exists(file_location) and count < 1000:
        count = count + 1
        filename = f"{base_name}_{count:03d}{extension}"
        file_location = os.path.join(upload_dir, filename)

    # save the file
    try:
        shutil.move(temp_file_path, file_location)

    except FileExistsError:
        # Catch the specific error raised by the 'xb' mode
        await file.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,  # 409
            detail=f"A file named '{filename}' already exists. Refusing to overwrite.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

    # Save image metadata in MySQL database
    file_path = os.path.join(parent_dirs, filename)
    db_image = PhotoModel(
        user_id=current_user.id,
        file_path=file_path,
        filename=file.filename,
        date_taken=date_taken,
        hash=img_hash,
        md5sum=md5sum,
        size=size,
        content_type=content_type,
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image
