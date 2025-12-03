from datetime import datetime
import hashlib
import os
from typing import List, Literal
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select
from PIL import Image, ImageOps
import imagehash
import io
import textwrap

from ..pagination import PaginatedResults

from .get_date import get_image_date
from ..settings import IMAGESIZES, MEDIADIR
from ..security import get_current_user
from ..schemas import PhotoSchema, PhotoUpdate
from ..models import PhotoModel, User
from ..database import get_db, update_data_in_db

router = APIRouter(
    prefix="/api/images",  # Sets the base path for all routes in this file
    tags=["images"],   # Groups these routes in the API docs (Swagger UI)
)

# Upload image endpoint
@router.post("/upload/", response_model=PhotoSchema)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    filename = str(file.filename)
    base_name, extension = os.path.splitext(filename)
    # get the image hash
    try:
        image_bytes = await file.read()
        md5sum = hashlib.md5(image_bytes).hexdigest()
        img = Image.open(io.BytesIO(image_bytes))
        img_hash = imagehash.average_hash(img)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

    # date
    date_taken = get_image_date(img, filename)

    # try and get exact matches
    dupe:PhotoModel|None = None
    dupe = db.query(PhotoModel).filter(and_(
        PhotoModel.hash == str(img_hash),
        PhotoModel.md5sum == md5sum
        )).first()
    
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
    db_image = PhotoModel(
        user_id=current_user.id, 
        file_path=file_path, 
        filename=file.filename,
        date_taken=date_taken, 
        hash=img_hash,
        md5sum=md5sum)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# Retrieve image metadata endpoint
@router.get("/{image_id}", response_model=PhotoSchema)
async def get_image(image_id: int, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    image = db.query(PhotoModel).filter(and_(PhotoModel.id == image_id, PhotoModel.user_id == current_user.id)).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

# Update the image metadata
@router.patch("/{image_id}", response_model=PhotoSchema)
async def update_image(image_id: int, photo: PhotoUpdate,  db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    db_image = db.query(PhotoModel).filter(and_(PhotoModel.id == image_id, PhotoModel.user_id == current_user.id)).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Item not found")
    update_data_in_db(db_image, photo)
    db.commit()
    db.refresh(db_image)
    return db_image

# Retrieve image file endpoint
@router.get("/files/{size}/{image_id}/{filename}")
async def get_image_file(size: str, image_id: int, filename: str, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    image = db.query(PhotoModel).filter(and_(PhotoModel.id == image_id, PhotoModel.user_id == current_user.id)).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    # construct the location
    userdir = os.path.join(MEDIADIR,str(current_user.id))
    file_location = os.path.join(userdir,image.file_path)

    if size in IMAGESIZES:
        filename = f"{image.id}_{size}.jpg"
        thumb_location = os.path.join(MEDIADIR,"cache",filename)
        if not os.path.exists(thumb_location):
            "create the thumbnail"
            os.makedirs(os.path.join(MEDIADIR,"cache"), exist_ok=True)
            with Image.open(file_location) as img:
                img_transposed = ImageOps.exif_transpose(img)
                img_transposed.thumbnail(IMAGESIZES[size], Image.Resampling.LANCZOS)
                img_transposed.save(thumb_location)
        return FileResponse(thumb_location)
    if size == "o":
        return FileResponse(file_location)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# Get a list of images
@router.get("/", response_model=PaginatedResults[PhotoSchema])
async def get_image_list(offset: int = 0, limit: int = 100, sortBy:Literal["date_taken", "date_uploaded", "date_updated"] = "date_taken", sortDescending: bool = False, after: datetime  | None = None, before: datetime  | None = None, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    filter_conditions = [PhotoModel.user_id == current_user.id]
    if after is not None:
        filter_conditions.append(PhotoModel.date_taken >= after)
    if before is not None:
        filter_conditions.append(PhotoModel.date_taken < before)

    #sort
    sort = PhotoModel.date_taken.asc()
    if sortBy == "date_taken":
        if sortDescending:
            sort = PhotoModel.date_taken.desc()
    if sortBy == "date_updated":
        sort = PhotoModel.date_updated.asc() 
        if sortDescending:
            sort = PhotoModel.date_taken.desc()
    if sortBy == "date_uploaded":
        sort = PhotoModel.date_uploaded.asc()
        if sortDescending:
            sort = PhotoModel.date_uploaded.desc()

    items_stmt = select(PhotoModel).where(and_(*filter_conditions)).offset(offset).limit(limit).order_by(sort)
    photo_list = db.execute(items_stmt).scalars().all()

    count_stmt = select(func.count()).select_from(PhotoModel).where(and_(*filter_conditions))
    total_count = db.execute(count_stmt).scalar()
    
    paginated_response = PaginatedResults[PhotoSchema](
        items=photo_list,
        total_count=total_count,
        offset=offset,
        limit=limit
    )
    
    return paginated_response