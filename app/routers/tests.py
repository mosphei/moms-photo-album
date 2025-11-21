import subprocess
from fastapi import APIRouter


router = APIRouter(
    prefix="/api/tests",  # Sets the base path for all routes in this file
    tags=["tests"],   # Groups these routes in the API docs (Swagger UI)
)
@router.get('/magick')
def get_magick():
    result = subprocess.run(["/usr/bin/identify",'-version'], capture_output=True)
    command_output = result.stdout
    return command_output