
import re
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db, update_data_in_db
from app.models import PersonCountModel, PersonModel, SearchPersonModel, User
from app.pagination import PaginatedResults
from app.routers.search import fuzz_people
from app.schemas import PersonCreate, PersonUpdate, PersonSchema
from app.security import get_current_user
from rapidfuzz import utils

from app.settings import MIN_RELEVANCE

router = APIRouter(
    prefix="/api/people",  
    tags=["people"],   
)


# Get a list of people
@router.get("/", response_model=PaginatedResults[PersonSchema])
async def get_people_list(q:str|None=None, offset: int = 0, limit: int = 100, sortBy:Literal["name"] = "name", sortDescending: bool = False, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    # sort
    sort = PersonCountModel.name.asc()
    if sortBy == "name":
        if sortDescending:
            sort = PersonCountModel.name.desc()
    
    # search
    items_stmt = select(PersonCountModel).offset(offset).limit(limit).order_by(sort)
    count_stmt = select(func.count()).select_from(PersonCountModel)
    if q is not None and len(q) > 1:
        term = utils.default_process(q)
        fuzz_people(term, db)
        items_stmt = (
            select(PersonCountModel)
            .outerjoin(
                SearchPersonModel,
                PersonCountModel.id == SearchPersonModel.person_id
            )
            .where(
                and_(
                    SearchPersonModel.q == term,
                    SearchPersonModel.relevance > MIN_RELEVANCE
                )
            )
        ).offset(offset).limit(limit).order_by(SearchPersonModel.relevance.desc(),sort)
        # count
        subquery = select(
            SearchPersonModel.person_id
            ).where(and_(
                SearchPersonModel.q == term,
                SearchPersonModel.relevance >= MIN_RELEVANCE
                )
            )
        count_stmt = count_stmt.filter(PersonCountModel.id.in_(subquery))
    
    person_list = db.execute(items_stmt).scalars().all()
    total_count = db.execute(count_stmt).scalar()
    
    paginated_response = PaginatedResults[PersonSchema](
        items=person_list,
        total_count=total_count,
        offset=offset,
        limit=limit
    )
    
    return paginated_response

@router.get("/{person_id}",response_model=PersonSchema)
def get_person_by_id(person_id:int, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    db_person = db.query(PersonCountModel).filter(PersonCountModel.id == person_id).first()
    if db_person is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_person

@router.post("/new", response_model=PersonSchema)
def add_person(person: PersonCreate, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    db_person = PersonModel(name=person.name, past_names=person.past_names)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

# Update the person record
@router.patch("/{person_id}", response_model=PersonSchema)
async def update_person(person_id: int, photo: PersonUpdate, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    # should restrict this to admins?
    db_person = db.query(PersonModel).filter(PersonModel.id == person_id).first()
    if db_person is None:
        raise HTTPException(status_code=404, detail="Item not found")
    update_data_in_db(db_person, photo)
    db.commit()
    db.refresh(db_person)
    return db_person