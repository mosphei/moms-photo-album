import os
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select
from PIL import Image
import imagehash
import io
import textwrap

from ..pagination import PaginatedResults

from .get_date import get_image_date

from ..security import get_current_user
#from .. import schemas, models, database # Note the relative imports
from ..schemas import PhotoSchema
from ..models import Photo, User
from ..database import get_db

router = APIRouter(
    prefix="/api/images",  # Sets the base path for all routes in this file
    tags=["images"],   # Groups these routes in the API docs (Swagger UI)
)

MEDIADIR = "/media"
SIZES = {
    "thumb":(128, 128),
    "medium": (800, 600),
    "large":(1920, 1080)
}

# Upload image endpoint
@router.post("/upload/", response_model=PhotoSchema)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    filename = str(file.filename)
    base_name, extension = os.path.splitext(filename)
    # get the image hash
    try:
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

    # date
    date_taken = get_image_date(img, filename)

    # try and get exact matches
    dupe:Photo|None = None
    img_hash = None
    try:
        img_hash = imagehash.average_hash(img)
        dupe = db.query(Photo).filter(Photo.hash == str(img_hash)).first()
    except Exception as e:
        """unable to get hash"""
        pass
    if not dupe is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409
            detail=f"duplicate of file {dupe.id}"
        )
    if date_taken:
        parent_dirs = os.path.join(f"{date_taken.year:04d}", f"{date_taken.month:02d}")
    else:
        " split it on the filename to avoid directories with too many files"
        
        left_12 = base_name[:12]
        chunks_list = textwrap.wrap(left_12, 4)
        parent_dirs = os.path.join(*chunks_list)

    upload_dir = os.path.join(MEDIADIR,str(current_user.id),parent_dirs)
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
        with open(file_location, "xb") as f:
            f.write(image_bytes)
    except FileExistsError:
        # Catch the specific error raised by the 'xb' mode
        await file.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409
            detail=f"A file named '{filename}' already exists. Refusing to overwrite."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")
    
    # Save image metadata in MySQL database
    file_path = os.path.join(parent_dirs,filename)
    db_image = Photo(user_id=current_user.id, file_path=file_path, date_taken=date_taken, hash=img_hash)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# Retrieve image metadata endpoint
@router.get("/{image_id}", response_model=PhotoSchema)
async def get_image(image_id: int, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    image = db.query(Photo).filter(and_(Photo.id == image_id, Photo.user_id == current_user.id)).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

# Retrieve image file endpoint
@router.get("/files/{size}/{image_id}/{filename}")
async def get_image_file(size: str, image_id: int, filename: str, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    image = db.query(Photo).filter(and_(Photo.id == image_id, Photo.user_id == current_user.id)).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    # construct the location
    userdir = os.path.join(MEDIADIR,str(current_user.id))
    file_location = os.path.join(userdir,image.file_path)

    if size == "thumb" or size == "medium" or size =="large":
        filename = f"{image.id}_{size}.jpg"
        thumb_location = os.path.join(MEDIADIR,"cache",filename)
        if not os.path.exists(thumb_location):
            "create the thumbnail"
            os.makedirs(os.path.join(MEDIADIR,"cache"), exist_ok=True)
            fullimg = Image.open(file_location)
            fullimg.thumbnail(SIZES[size], Image.Resampling.LANCZOS)
            fullimg.save(thumb_location)
        return FileResponse(thumb_location)
    if size == "o":
        return FileResponse(file_location)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# Get a list of images
@router.get("/", response_model=PaginatedResults[PhotoSchema])
async def get_image_list(q: str | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    
    count_stmt = select(func.count()).select_from(User)
    total_count = db.execute(count_stmt).scalar() or 0
    
    stmt = select(Photo).filter(Photo.user_id == current_user.id).offset(skip).limit(limit)
    photo_list = db.execute(stmt).scalars().all()
    retval: PaginatedResults[PhotoSchema] = PaginatedResults(
        total_count= total_count,
        items= [],
        offset= skip,
        limit= limit
    )