from datetime import datetime
import os
import shutil
from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, select
from PIL import Image, ImageOps
from rapidfuzz import utils


from app.media_utils import create_video_thumbnail
from app.routers.search import fuzz_photos

from ..pagination import PaginatedResults

from ..settings import IMAGESIZES, MEDIADIR, MEDIATYPES, MIN_RELEVANCE
from ..security import get_current_user
from ..schemas import PhotoSchema, PhotoUpdate
from ..models import (
    PhotoModel,
    photo_person_association,
    SearchPhotoModel,
    User,
    PersonModel,
)
from ..database import get_db

router = APIRouter(
    prefix="/api/images",  # Sets the base path for all routes in this file
    tags=["images"],  # Groups these routes in the API docs (Swagger UI)
)


# Retrieve image metadata endpoint
@router.get("/{image_id}", response_model=PhotoSchema)
async def get_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = (
        db.query(PhotoModel)
        .filter(and_(PhotoModel.id == image_id, PhotoModel.user_id == current_user.id))
        .first()
    )
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


# Update the image metadata
@router.patch("/{photo_id}", response_model=PhotoSchema)
async def update_image(
    photo_id: int,
    photo_update: PhotoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch the existing photo
    photo = db.query(PhotoModel).filter(PhotoModel.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Update the fields if provided in the request body
    if photo_update.filename is not None:
        photo.filename = photo_update.filename
    if photo_update.date_taken is not None:
        photo.date_taken = photo_update.date_taken
    if photo_update.date_uploaded is not None:
        photo.date_uploaded = photo_update.date_uploaded
    if photo_update.description is not None:
        photo.description = photo_update.description

    # Update the people associated with the photo (if provided)
    if photo_update.people is not None:
        photo.people.clear()
        for person in photo_update.people:
            db_person = (
                db.query(PersonModel).filter(PersonModel.id == person.id).first()
            )
            if db_person:
                photo.people.append(db_person)
            else:
                raise HTTPException(
                    status_code=404, detail=f"Person with id {person.id} not found"
                )
    # any image manipulations?
    if photo_update.rotation is not None and photo_update.rotation != 0:
        print(f"rotation:{photo_update.rotation}")
        file_location = os.path.join(MEDIADIR, str(current_user.id), photo.file_path)
        image = Image.open(file_location)
        rotated_img = image.rotate(photo_update.rotation, expand=True)
        rotated_img.save(file_location)
        # delete any thumbnails etc
        for size in IMAGESIZES:
            filename = f"{photo.id}_{size}.jpg"
            cache_location = os.path.join(MEDIADIR, "cache", filename)
            if os.path.exists(cache_location):
                os.remove(cache_location)
    # Commit the changes to the database
    db.commit()
    db.refresh(photo)
    return photo


# Delete!
@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo = db.query(PhotoModel).filter(PhotoModel.id == photo_id).first()
    if not photo is None:
        file_path = os.path.join(MEDIADIR, str(current_user.id), photo.file_path)
        if os.path.exists(file_path):
            basename, ext = os.path.splitext(photo.filename)
            trashbin = os.path.join(MEDIADIR, "trash", str(current_user.id))
            os.makedirs(trashbin, exist_ok=True)
            photo_filename = f"{photo.id:04d}{ext}"
            data_filename = f"{photo.id:04d}.json"
            with open(os.path.join(trashbin, data_filename), "w") as json_file:
                photoSchema = PhotoSchema.model_validate(photo)
                json_string = photoSchema.model_dump_json(indent=4)
                json_file.write(json_string)
            shutil.move(file_path, os.path.join(trashbin, photo_filename))
        # delete from database too
        db.delete(photo)
        db.commit()
        # finally get rid of any thumbnails etc
        for size in IMAGESIZES:
            filename = f"{photo.id}_{size}.jpg"
            cache_location = os.path.join(MEDIADIR, "cache", filename)
            if os.path.exists(cache_location):
                os.remove(cache_location)


# Retrieve image file endpoint
@router.get("/files/{size}/{image_id}/{filename}")
async def get_image_file(
    size: str,
    image_id: int,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_photo = (
        db.query(PhotoModel)
        .filter(and_(PhotoModel.id == image_id, PhotoModel.user_id == current_user.id))
        .first()
    )
    if not db_photo:
        raise HTTPException(status_code=404, detail="Image not found")
    # construct the location
    userdir = os.path.join(MEDIADIR, str(current_user.id))
    file_location = os.path.join(userdir, db_photo.file_path)

    if size in IMAGESIZES:
        filename = f"{db_photo.id}_{size}.jpg"
        thumb_location = os.path.join(MEDIADIR, "cache", filename)
        if not os.path.exists(thumb_location):
            "create the thumbnail"
            os.makedirs(os.path.join(MEDIADIR, "cache"), exist_ok=True)
            if str(db_photo.content_type).startswith("video/"):
                # ffmpeg?
                width, height = IMAGESIZES[size]
                create_video_thumbnail(file_location, thumb_location, width, -1)
            else:
                # image
                basename, ext = os.path.splitext(db_photo.filename)
                if ext.lower() in MEDIATYPES["image"]:
                    with Image.open(file_location) as img:
                        img_transposed = ImageOps.exif_transpose(img)
                        img_transposed.thumbnail(
                            IMAGESIZES[size], Image.Resampling.LANCZOS
                        )
                        img_transposed.save(thumb_location)
        return FileResponse(thumb_location)
    if size == "o":
        return FileResponse(file_location)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# Get a list of images
@router.get("/", response_model=PaginatedResults[PhotoSchema])
async def get_image_list(
    q: str | None = None,
    person_id: Optional[List[int]] = Query(default=None),
    offset: int = 0,
    limit: int = 100,
    sortBy: Literal["date_taken", "date_uploaded", "date_updated"] = "date_taken",
    sortDescending: bool = False,
    after: datetime | None = None,
    before: datetime | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filter_conditions = [PhotoModel.user_id == current_user.id]
    if after is not None:
        filter_conditions.append(PhotoModel.date_taken >= after)
    if before is not None:
        filter_conditions.append(PhotoModel.date_taken < before)
    if person_id is not None:
        for p_id in person_id:
            subquery = select(photo_person_association.c.photo_id).where(
                photo_person_association.c.person_id == p_id
            )
            print(subquery)
            filter_conditions.append(PhotoModel.id.in_(subquery))

    # sort
    sort = PhotoModel.date_taken.asc()
    if sortBy == "date_taken":
        if sortDescending:
            sort = PhotoModel.date_taken.desc()
    if sortBy == "date_updated":
        sort = PhotoModel.date_updated.asc()
        if sortDescending:
            sort = PhotoModel.date_taken.desc()
    if sortBy == "date_uploaded":
        sort = PhotoModel.date_uploaded.asc()
        if sortDescending:
            sort = PhotoModel.date_uploaded.desc()

    items_stmt = (
        select(PhotoModel)
        .where(and_(*filter_conditions))
        .offset(offset)
        .limit(limit)
        .order_by(sort)
    )
    count_stmt = (
        select(func.count()).select_from(PhotoModel).where(and_(*filter_conditions))
    )
    if q is not None:
        q_filter_value = utils.default_process(q)
        if q_filter_value is not None:
            # preload the search
            fuzz_photos(q_filter_value, filter_conditions, db)
            # change the query
            items_stmt = (
                select(PhotoModel, SearchPhotoModel.relevance)
                .outerjoin(
                    SearchPhotoModel,
                    # Define the ON clause for the join
                    and_(
                        PhotoModel.id == SearchPhotoModel.photo_id,
                        SearchPhotoModel.q == q_filter_value,
                    ),
                )
                .where(
                    and_(*filter_conditions, SearchPhotoModel.relevance > MIN_RELEVANCE)
                )
                .offset(offset)
                .limit(limit)
                .order_by(SearchPhotoModel.relevance.desc(), sort)
            )

            # count
            count_stmt = (
                select(func.count())
                .select_from(PhotoModel)
                .outerjoin(
                    SearchPhotoModel,
                    # Define the ON clause for the join
                    and_(
                        PhotoModel.id == SearchPhotoModel.photo_id,
                        SearchPhotoModel.q == q_filter_value,
                    ),
                )
                .where(
                    and_(*filter_conditions, SearchPhotoModel.relevance > MIN_RELEVANCE)
                )
            )

    print(items_stmt)
    photo_list = db.execute(items_stmt).scalars().all()
    total_count = db.execute(count_stmt).scalar()

    paginated_response = PaginatedResults[PhotoSchema](
        items=photo_list, total_count=total_count, offset=offset, limit=limit
    )

    return paginated_response
