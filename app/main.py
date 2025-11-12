import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from database import DATABASE_URL
from models import Base, Image
from schemas import ImageCreate, ImageSchema

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_recycle=3600)

# Create the session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables (if they don't exist)
Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Upload image endpoint
@app.post("/upload/", response_model=ImageSchema)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save file to disk (you can later update this to store files in cloud storage)
    upload_dir = "static/images/"
    os.makedirs(upload_dir, exist_ok=True)
    file_location = os.path.join(upload_dir, file.filename)
    
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Save image metadata in MySQL database
    db_image = Image(file_path=file_location)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image

# Retrieve image metadata endpoint
@app.get("/images/{image_id}", response_model=ImageSchema)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

# Retrieve image file endpoint
@app.get("/files/{image_id}")
async def get_image_file(image_id: int, db: Session = Depends(get_db)):
    imagepath = db.query(Image.file_path).filter(Image.id == image_id).first()
    if not imagepath:
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(imagepath[0])
