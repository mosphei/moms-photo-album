import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import create_all_tables, get_db
from models import Base, Image
from schemas import ImageCreate, ImageSchema
from .routers import images

create_all_tables()

# Create FastAPI instance
app = FastAPI()

app.include_router(images.router)

@app.get("/cwd")
def read_cwd():
    return os.getcwd()