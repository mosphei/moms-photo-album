import subprocess
from fastapi import APIRouter


router = APIRouter(
    prefix="/api/tests",  # Sets the base path for all routes in this file
    tags=["tests"],   # Groups these routes in the API docs (Swagger UI)
)
@router.get('/magick')
def get_magick():
    details = {}
    result = subprocess.run(["/usr/bin/identify",'-version'], capture_output=True)
    details['imagemagick'] = result.stdout
    # get an image info
    result = subprocess.run(["identify", "-verbose", "/media/images/1/IMG_20210902_152610.jpg"], capture_output=True)
    details['image']=result
    return details