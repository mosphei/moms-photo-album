import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import create_all_tables
from .routers import admin, images, people, search, upload, users, tests

create_all_tables()

# Create FastAPI instance
app = FastAPI()
app.include_router(admin.router)
app.include_router(images.router)
app.include_router(people.router)
app.include_router(search.router)
app.include_router(upload.router)
app.include_router(users.router)
app.include_router(tests.router)


@app.get("/api/cwd")
def read_cwd():
    "get cuurent dir"
    return os.getcwd()


@app.get("/favicon.ico")
async def about_page():
    return FileResponse("static/favicon.ico")


app.mount("/_app", StaticFiles(directory="/app/static/_app", html=True), name="static")


# everything else
@app.get("/{file_path:path}")
async def spa():
    return FileResponse("static/index.html")
