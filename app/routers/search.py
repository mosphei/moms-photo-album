
from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, desc, func, nulls_last, or_, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import PhotoModel, User, SearchPhotoModel
from app.pagination import PaginatedResults
from app.schemas import PhotoSchema
from app.security import get_current_user
from rapidfuzz import fuzz, utils

router = APIRouter(
    prefix="/api/search",  
    tags=["search"],   
)

@router.get("/images")
async def search_images(q: str,offset: int = 0, limit: int = 100, sortBy:Literal["date_taken", "date_uploaded", "date_updated", "relevance"] = "relevance", sortDescending: bool = False, after: datetime  | None = None, before: datetime  | None = None, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    filter_conditions = [PhotoModel.user_id == current_user.id]
    if after is not None:
        filter_conditions.append(PhotoModel.date_taken >= after)
    if before is not None:
        filter_conditions.append(PhotoModel.date_taken < before)

    # do the fuzzy
    q_filter_value = utils.default_process(q)
    if q_filter_value =="":
        raise HTTPException(status_code=409,detail="invalid search")
    subquery = (
        select(SearchPhotoModel.photo_id)
        .where(SearchPhotoModel.q == q_filter_value)
        .scalar_subquery() # Makes this select usable as a scalar value source (e.g., in a NOT IN clause)
    )
    query = (
        select(PhotoModel)
        # Perform an outer join between PhotoModel and SearchPhotoModel on ID and 'q' value
        .outerjoin(
            SearchPhotoModel,
            and_(
                PhotoModel.id == SearchPhotoModel.photo_id,
                SearchPhotoModel.q == q_filter_value,
                *filter_conditions
            )
        )
        .where(
            or_(
                # Condition A: The photo is entirely missing from SearchPhotoModel for this 'q'
                SearchPhotoModel.photo_id.is_(None),

                # Condition B: The existing entry has a date_seen older than the photo's last update
                SearchPhotoModel.date_seen < PhotoModel.date_updated
            )
        )
        
    )
    photos_to_process = db.execute(query).scalars().all()
    for photo in photos_to_process:
        srcresult=SearchPhotoModel()
        srcresult.photo_id = photo.id
        srcresult.q = q_filter_value
        srcresult.relevance = 0
        if photo.description is not None:
            srcresult.relevance = fuzz.WRatio(q_filter_value, photo.description, processor=utils.default_process)
        if photo.filename is not None:
            ratio = fuzz.WRatio(q_filter_value, photo.filename, processor=utils.default_process)
            if (ratio > srcresult.relevance):
                srcresult.relevance = ratio
        db.add(srcresult)
    db.commit()
    #sort
    sort = desc(SearchPhotoModel.relevance)
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
    # do the query
    query = (
        select(PhotoModel, SearchPhotoModel.relevance)
        # Perform a LEFT OUTER JOIN
        .outerjoin(
            SearchPhotoModel,
            # Define the ON clause for the join
            and_(
                PhotoModel.id == SearchPhotoModel.photo_id, 
                SearchPhotoModel.q == q_filter_value,
                *filter_conditions
                )
        )
        # Use nulls_last() to ensure photos without a relevance score appear at the end.
        .order_by(
            sort
        )
        .offset(offset).limit(limit)
    )
    photo_list = db.execute(query).scalars().all()
    count_stmt = select(func.count()).select_from(PhotoModel).where(and_(*filter_conditions))
    total_count = db.execute(count_stmt).scalar()

    # count em
    paginated_response = PaginatedResults[PhotoSchema](
        items=photo_list,
        total_count=total_count,
        offset=offset,
        limit=limit
    )
    return paginated_response

@router.get("/")
async def search_all(q: str,current_user=Depends(get_current_user)):
    return current_user.id

@router.get('/test')
async def get_test():
    return fuzz.ratio("this is a test", "this is a test!")