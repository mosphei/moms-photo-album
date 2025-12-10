
from datetime import datetime
import time
from typing import Generic, List, Literal, TypeVar
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, desc, func, nulls_last, or_, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import PersonCountModel, PersonModel, PhotoModel, SearchPersonModel, User, SearchPhotoModel
from app.pagination import PaginatedResults
from app.schemas import PersonSchema, PersonSearchResult, PhotoSchema
from app.security import get_current_user
from rapidfuzz import fuzz, utils
from rapidfuzz.fuzz import WRatio as compare

from app.settings import MIN_RELEVANCE

from pydantic.generics import GenericModel

# Define a Type Variable (T is a common convention)
T = TypeVar('T')

# Define the generic class, inheriting from GenericModel and Generic[T]
class SearchResult(GenericModel, Generic[T]):
    item: T
    relevance: float 

router = APIRouter(
    prefix="/api/search",  
    tags=["search"],   
)

@router.get("/people", response_model=PaginatedResults[PersonSearchResult])
async def search_people(q: str,offset: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    q_filter_value = utils.default_process(q)
    if q_filter_value =="":
        raise HTTPException(status_code=409,detail="invalid search")
    print("# delete outdated entries")
    start_time = time.perf_counter()
    query=select(
        SearchPersonModel
        ).outerjoin(
            PersonModel,
            and_(
                PersonModel.id == SearchPersonModel.person_id
            )
        ).where(
            SearchPersonModel.date_seen < PersonModel.date_updated
        )
    outdated = db.execute(query).scalars().all()
    for spm in outdated:
        db.delete(spm)

    elapsed_seconds = time.perf_counter() - start_time
    print(f"### {elapsed_seconds} sec")
    print("# find missing entries")
    start_time = time.perf_counter()
    query = (
        select(PersonModel)
        .outerjoin(
            SearchPersonModel,
            and_(
                PersonModel.id == SearchPersonModel.person_id,
                SearchPersonModel.q == q_filter_value,
            )
        )
        .where(
            or_(
                SearchPersonModel.person_id.is_(None),
                SearchPersonModel.date_seen < PersonModel.date_updated
            )
        )
    )
    persons_to_process = db.execute(query).scalars().all()
    elapsed_seconds = time.perf_counter() - start_time
    print(f"### {elapsed_seconds} sec")

    start_time = time.perf_counter()
    print(f"to process:{len(persons_to_process)}")
    for row in persons_to_process:
        spm = SearchPersonModel(person_id=row.id, q=q, relevance=0)
        spm.relevance = compare(q, str(row.name), processor=utils.default_process)
        if row.past_names is not None:
            ratio = compare(q, str(row.past_names), processor=utils.default_process)
            if ratio > spm.relevance:
                spm.relevance = ratio
        db.add(spm)
    db.commit()
    elapsed_seconds = time.perf_counter() - start_time
    print(f"### {elapsed_seconds} sec")

    print("# do the query")
    start_time = time.perf_counter()
    query = (
        select(PersonModel, SearchPersonModel.relevance)
        .outerjoin(
            SearchPersonModel,
            PersonModel.id == SearchPersonModel.person_id
        )
        .where(
            and_(
                SearchPersonModel.q == q_filter_value,
                SearchPersonModel.relevance > MIN_RELEVANCE
            )
        )
        .order_by(desc(SearchPersonModel.relevance))
        .offset(offset).limit(limit)
    )
    print(query)
    rows =  db.execute(query).all()
    
    elapsed_seconds = time.perf_counter() - start_time
    print(f"### {elapsed_seconds} sec")
    
    person_list=[]
    for row, x in rows:
        print(f"row:{row},{x}")
        entry = PersonSearchResult.model_validate(row)
        entry.relevance = x
        person_list.append(entry)
    
    count_stmt = select(func.count()).select_from(SearchPersonModel).where(
            and_(
                SearchPersonModel.q == q_filter_value,
                SearchPersonModel.relevance > MIN_RELEVANCE
            )
        )
    total_count = db.execute(count_stmt).scalar()

    # count em
    paginated_response = PaginatedResults[PersonSearchResult](
        items=person_list,
        total_count=total_count,
        offset=offset,
        limit=limit
    )
    return paginated_response

    
@router.get("/images")
async def search_images(q: str,offset: int = 0, limit: int = 100, sortBy:Literal["date_taken", "date_uploaded", "date_updated", "relevance"] = "relevance", sortDescending: bool = False, after: datetime  | None = None, before: datetime  | None = None, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    filter_conditions = [PhotoModel.user_id == current_user.id]
    if after is not None:
        filter_conditions.append(PhotoModel.date_taken >= after)
    if before is not None:
        filter_conditions.append(PhotoModel.date_taken < before)

    # do the fuzzy
    q_filter_value = utils.default_process(q)
    if q_filter_value == "":
        raise HTTPException(status_code=409,detail="invalid search")
    # delete any calulations older than date_updated
    query=select(
        SearchPhotoModel
        ).outerjoin(
            PhotoModel,
            and_(
                PhotoModel.id == SearchPhotoModel.photo_id
            )
        ).where(
            SearchPhotoModel.date_seen < PhotoModel.date_updated
        )
    outdated = db.execute(query).scalars().all()
    for spm in outdated:
        db.delete(spm)
    query = (
        select(PhotoModel)
        .outerjoin(
            SearchPhotoModel,
            and_(
                PhotoModel.id == SearchPhotoModel.photo_id,
                SearchPhotoModel.q == q_filter_value
            )
        )
        .where(
            and_(
                or_(
                    SearchPhotoModel.photo_id.is_(None),
                    SearchPhotoModel.date_seen < PhotoModel.date_updated
                ),
                *filter_conditions
            )
        )
    )
    print(str(query))
    photos_to_process = db.execute(query).scalars().all()
    print(f"len(photos_to_process={len(photos_to_process)})")
    for photo in photos_to_process:
        srcresult=SearchPhotoModel()
        srcresult.photo_id = photo.id
        srcresult.q = q_filter_value
        srcresult.relevance = 0
        if photo.description is not None:
            srcresult.relevance = compare(q_filter_value, photo.description, processor=utils.default_process)
        if photo.filename is not None:
            ratio = compare(q_filter_value, photo.filename, processor=utils.default_process)
            if (ratio > srcresult.relevance):
                srcresult.relevance = ratio
        
        if len(photo.people) > 0:
            names_list = [str(person.name) for person in photo.people]
            joined_names = ", ".join(names_list)
            ratio = compare(q, joined_names)
            print(f"{ratio} =ratio({q},{joined_names})")
            if ratio > srcresult.relevance:
                srcresult.relevance = ratio
            if srcresult.relevance < MIN_RELEVANCE:
                names_list = [str(person.name) for person in photo.people]
                joined_names = ", ".join(names_list)
                ratio = compare(q, joined_names)
                if ratio > srcresult.relevance:
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
                SearchPhotoModel.q == q_filter_value
                )
        )
        .where(and_(*filter_conditions,SearchPhotoModel.relevance > MIN_RELEVANCE))
        # Use nulls_last() to ensure photos without a relevance score appear at the end.
        .order_by(
            sort
        )
        .offset(offset).limit(limit)
    )
    photo_list = db.execute(query).scalars().all()
    count_stmt = select(func.count()).select_from(PhotoModel).outerjoin(
            SearchPhotoModel,
            # Define the ON clause for the join
            and_(
                PhotoModel.id == SearchPhotoModel.photo_id, 
                SearchPhotoModel.q == q_filter_value
                )
        ).where(and_(*filter_conditions,SearchPhotoModel.relevance > MIN_RELEVANCE))
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
async def get_test(s1: str, s2: str):
    return {
        "ratio":fuzz.ratio(s1,s2, processor=utils.default_process),
        "partial_ratio": fuzz.partial_ratio(s1,s2, processor=utils.default_process),
        "WRatio":fuzz.WRatio(s1,s2, processor=utils.default_process),
        "token_ratio":fuzz.token_ratio(s1,s2, processor=utils.default_process),
        "token_set_ratio": fuzz.token_set_ratio(s1,s2, processor=utils.default_process),
        "QRatio": fuzz.QRatio(s1,s2, processor=utils.default_process),
        "partial_token_ratio": fuzz.partial_token_ratio(s1,s2, processor=utils.default_process),
        "token_sort_ratio": fuzz.token_sort_ratio(s1,s2, processor=utils.default_process),
    }