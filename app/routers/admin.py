import json
import os
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Base, PhotoModel, User, MissingPhotoModel
from app.pagination import PaginatedResults
from app.schemas import PhotoSchema
from app.security import get_current_user
from app.settings import MEDIADIR


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
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
