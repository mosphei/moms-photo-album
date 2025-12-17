from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import time
from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, status
import imagehash
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session
from PIL import Image

from app.database import get_db
from app.media_utils import (
    extract_creation_time,
    get_content_type_by_extension,
    get_date_from_filename,
    get_image_date,
    get_metadata_ffmpeg_python,
    make_photo_from_file,
)
from app.models import Base, PhotoModel, User, MissingPhotoModel
from app.pagination import PaginatedResults
from app.schemas import PhotoSchema, UserSchema
from app.security import get_current_user, hash_password
from app.settings import MEDIADIR


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
)


def assert_admin(current_user: User):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Must be admin",
        )


@router.get("/missing", response_model=PaginatedResults[PhotoSchema])
async def get_missing_photos(
    offset: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Must be admin",
        )

    maxid = db.execute(select(func.max(MissingPhotoModel.id))).scalar()
    if maxid is None:
        maxid = 0
    # search for more missing photos
    query = (
        select(PhotoModel).where(PhotoModel.id > maxid).order_by(PhotoModel.id.asc())
    )
    all_photos = db.execute(query).yield_per(100)
    missing_photos: List[PhotoModel] = list()
    max_time = 3  # seconds
    start_time = time.perf_counter()
    for photo in all_photos.scalars():
        file_path = os.path.join(MEDIADIR, str(photo.user_id), photo.file_path)
        if not os.path.exists(file_path):
            missing_photos.append(photo)
        if time.perf_counter() - start_time > max_time:
            break
    all_photos.close()
    for photo in missing_photos:
        photo_dict = photo.to_dict()
        json_string = json.dumps(photo_dict, indent=4)
        missing = MissingPhotoModel(id=photo.id, photo=json_string)
        db.add(missing)
        db.delete(photo)
    db.commit()

    # now query missing
    db_missing = (
        db.execute(
            select(MissingPhotoModel)
            .order_by(MissingPhotoModel.id)
            .offset(offset)
            .limit(limit)
        )
        .scalars()
        .all()
    )

    items = (PhotoSchema.model_validate_json(item.photo) for item in db_missing)
    count_stmt = select(func.count()).select_from(MissingPhotoModel)
    total_count = db.execute(count_stmt).scalar()

    return PaginatedResults[PhotoSchema](
        items=items, offset=offset, limit=limit, total_count=total_count
    )


@router.get("/scan", response_model=PaginatedResults[PhotoSchema])
async def scan_for_new_photos(
    offset: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assert_admin(current_user)
    items = []

    # just get user_id folders
    db_users = db.execute(select(User)).scalars().all()
    for user in db_users:
        user_folder = Path(os.path.join(MEDIADIR, str(user.id)))
        for file_path in user_folder.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(user_folder))
                # check if
                query = select(PhotoModel).where(
                    and_(
                        PhotoModel.user_id == user.id,
                        PhotoModel.file_path == relative_path,
                    )
                )
                db_photo = db.execute(query).first()
                if db_photo is None:
                    # woo add this one.
                    photo = make_photo_from_file(user.id, relative_path)
                    db.add(photo)
                    db.commit()
                    db.refresh(photo)
                    items.append(photo)
        if len(items) > limit:
            break

    return PaginatedResults[PhotoSchema](
        items=items, offset=offset, limit=limit, total_count=-1
    )


@router.get("/users", response_model=PaginatedResults[UserSchema])
def get_user_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: int = 10,
):
    assert_admin(current_user)

    db_users = (
        db.execute(select(User).order_by(User.username).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    total_users = db.execute(select(func.count()).select_from(User)).scalar()
    return PaginatedResults[UserSchema](
        items=db_users, offset=offset, limit=limit, total_count=total_users
    )


@router.get("/users/{username}", response_model=UserSchema)
def get_user(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assert_admin(current_user)

    db_user = db.execute(select(User).where(User.username == username)).scalar()
    if db_user is None:
        raise HTTPException(status_code=404, detail="No such user")
    return db_user


@router.post("/users/", response_model=UserSchema)
def update_user(
    username: str = Form(...),
    id: int = Form(...),
    password=Form(None),
    admin: bool | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assert_admin(current_user)
    db_user = db.execute(
        select(User).where(and_(User.id == id, User.username == username))
    ).scalar()
    if db_user is None:
        raise HTTPException(status_code=404, detail="no such user " + username)
    if admin is not None:
        db_user.admin = admin
    if password is not None:
        if len(password) < 10:
            raise HTTPException(status_code=422, detail="Password too short")
        db_user.hashed_password = hash_password(password)
    db.commit()
    db.refresh(db_user)
    return db_user
