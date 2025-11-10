from fastapi import FastAPI
import os
from . import database

database.create_all_tables()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World."}


@app.get("/cwd")
def read_cwd():
    return os.getcwd()
