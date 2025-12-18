import os
import subprocess
from fastapi import APIRouter


router = APIRouter(
    prefix="/api/tests",  # Sets the base path for all routes in this file
    tags=["tests"],  # Groups these routes in the API docs (Swagger UI)
)

APP_ENV = os.getenv("APP_ENV", "production")


@router.get("/env")
def get_env():
    return {APP_ENV: APP_ENV}
