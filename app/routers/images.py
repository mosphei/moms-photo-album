import os
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
import PIL 
import imagehash
import io

from ..security import get_current_user
#from .. import schemas, models, database # Note the relative imports
from ..schemas import ImageSchema
from ..models import Image, User
from ..database import get_db

router = APIRouter(
    prefix="/api/images",  # Sets the base path for all routes in this file
    tags=["images"],   # Groups these routes in the API docs (Swagger UI)
)

MEDIADIR = "/media"

# Upload image endpoint
@router.post("/upload/", response_model=ImageSchema)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    # Save file to disk (you can later update this to store files in cloud storage)
    upload_dir = f"/media/images/{current_user.id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_location = os.path.join(upload_dir, str(file.filename))
    # get the image hash
    try:
        image_bytes = await file.read()
        img = PIL.Image.open(io.BytesIO(image_bytes))
        img_hash = imagehash.average_hash(img)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

    with open(file_location, "wb") as f:
        f.write(image_bytes)
    
    # Save image metadata in MySQL database
    db_image = Image(file_path=file_location, hash=img_hash)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# Retrieve image metadata endpoint
@router.get("/{image_id}", response_model=ImageSchema)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

# Retrieve image file endpoint
@router.get("/files/{image_id}")
async def get_image_file(image_id: int, db: Session = Depends(get_db)):
    imagepath = db.query(Image.file_path).filter(Image.id == image_id).first()
    if not imagepath:
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(imagepath[0])

# Get a list of images
@router.get("/", response_model=List[ImageSchema])
async def get_image_list(q: str | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stmt = select(Image).offset(skip).limit(limit)
    result = db.execute(stmt).scalars().all()
    return result