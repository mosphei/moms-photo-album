from datetime import datetime
import hashlib
import json
import os
import shutil
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
from ..settings import IMAGESIZES, MEDIADIR, MEDIATYPES
from ..security import get_current_user
from ..schemas import PhotoSchema, PhotoUpdate
from ..models import PhotoModel, User, PersonModel
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
    
    # try and get exact matches
    dupe:PhotoModel|None = None
    dupe = db.query(PhotoModel).filter(and_(
        PhotoModel.hash == str(img_hash),
        PhotoModel.md5sum == md5sum
        )).first()
    
    if not dupe is None:
        #this file has already been uploaded
        return dupe
    
    # date
    date_taken = get_image_date(img, filename)
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
@router.patch("/{photo_id}", response_model=PhotoSchema)
async def update_image(photo_id: int, photo_update: PhotoUpdate,  db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    # Fetch the existing photo
    photo = db.query(PhotoModel).filter(PhotoModel.id == photo_id).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Update the fields if provided in the request body
    if photo_update.filename is not None:
        photo.filename = photo_update.filename
    if photo_update.date_taken is not None:
        photo.date_taken = photo_update.date_taken
    if photo_update.date_uploaded is not None:
        photo.date_uploaded = photo_update.date_uploaded
    if photo_update.description is not None:
        photo.description = photo_update.description
    
    # Update the people associated with the photo (if provided)
    if photo_update.people is not None:
        photo.people.clear()
        for person in photo_update.people:
            db_person = db.query(PersonModel).filter(PersonModel.id == person.id).first()
            if db_person:
                photo.people.append(db_person)
            else:
                raise HTTPException(status_code=404, detail=f"Person with id {person.id} not found")
    # any image manipulations?
    if photo_update.rotation is not None and photo_update.rotation != 0:
        print(f"rotation:{photo_update.rotation}")
        file_location = os.path.join(MEDIADIR,str(current_user.id),photo.file_path)
        image = Image.open(file_location)
        rotated_img = image.rotate(photo_update.rotation, expand=True)
        rotated_img.save(file_location)
        # delete any thumbnails etc
        for size in IMAGESIZES:
            filename = f"{photo.id}_{size}.jpg"
            cache_location = os.path.join(MEDIADIR,"cache",filename)
            if os.path.exists(cache_location):
                os.remove(cache_location)
    # Commit the changes to the database
    db.commit()    
    db.refresh(photo)
    return photo

# Delete!
@router.delete("/{photo_id}")
async def delete_photo(photo_id: int, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    photo = db.query(PhotoModel).filter(PhotoModel.id == photo_id).first()
    if not photo is None:
        file_path=os.path.join(MEDIADIR,str(current_user.id),photo.file_path)
        if os.path.exists(file_path):
            basename, ext = os.path.splitext(photo.filename)
            trashbin=os.path.join(MEDIADIR,'trash',str(current_user.id))
            os.makedirs(trashbin, exist_ok=True)
            photo_filename=f"{photo.id:04d}{ext}"
            data_filename=f"{photo.id:04d}.json"
            with open(os.path.join(trashbin,data_filename), 'w') as json_file:
                photoSchema=PhotoSchema.model_validate(photo)
                json_string = photoSchema.model_dump_json(indent=4)
                json_file.write(json_string)
            shutil.move(file_path,os.path.join(trashbin,photo_filename))
        # delete from database too
        db.delete(photo)
        db.commit()
        # finally get rid of any thumbnails etc
        for size in IMAGESIZES:
            filename = f"{photo.id}_{size}.jpg"
            cache_location = os.path.join(MEDIADIR,"cache",filename)
            if os.path.exists(cache_location):
                os.remove(cache_location)

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
            basename, ext = os.path.splitext(image.filename)
            if ext.lower() in MEDIATYPES["image"]:
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