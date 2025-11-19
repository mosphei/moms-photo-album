import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
#from .. import schemas, models, database # Note the relative imports
from ..schemas import ImageSchema
from ..models import Image
from ..database import get_db

router = APIRouter(
    prefix="/api/images",  # Sets the base path for all routes in this file
    tags=["images"],   # Groups these routes in the API docs (Swagger UI)
)

MEDIADIR = "/media"

# Upload image endpoint
@router.post("/upload/", response_model=ImageSchema)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save file to disk (you can later update this to store files in cloud storage)
    upload_dir = "/media/images/"
    os.makedirs(upload_dir, exist_ok=True)
    file_location = os.path.join(upload_dir, str(file.filename))
    
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Save image metadata in MySQL database
    db_image = Image(file_path=file_location)
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
