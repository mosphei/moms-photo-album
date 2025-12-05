import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import create_all_tables, get_db
from models import Base, PhotoModel
from schemas import PhotoCreate, PhotoSchema
from .routers import images, people, users, tests

create_all_tables()

# Create FastAPI instance
app = FastAPI()
app.include_router(images.router)
app.include_router(people.router)
app.include_router(users.router)
app.include_router(tests.router)

@app.get("/api/cwd")
def read_cwd():
    "get cuurent dir"
    return os.getcwd()


app.mount("/", StaticFiles(directory="/app/static", html=True), name="static")
