import os
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
import PIL 
import imagehash
import io
import textwrap

from .get_date import get_image_date

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
    filename = str(file.filename)
    
    
    # get the image hash
    try:
        image_bytes = await file.read()
        img = PIL.Image.open(io.BytesIO(image_bytes))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

    # date
    date_taken = get_image_date(img, filename)

    # try and get exact matches
    try:
                
        img_hash = imagehash.average_hash(img)
    except Exception as e:
        """unable to get hash"""
        pass
    if date_taken:
        parent_dirs = os.path.join(f"{date_taken.year:04d}", f"{date_taken.month:02d}")
    else:
        " split it on the filename to avoid directories with too many files"
        base_name, extension = os.path.splitext(filename)
        left_12 = base_name[:12]
        chunks_list = textwrap.wrap(left_12, 4)
        parent_dirs = os.path.join(*chunks_list)
    upload_dir = os.path.join(MEDIADIR,str(current_user.id),parent_dirs)
    os.makedirs(upload_dir, exist_ok=True)
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
    db_image = Image(file_path=file_location, date_taken=date_taken)
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