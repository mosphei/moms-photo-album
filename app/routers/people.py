
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.database import get_db, update_data_in_db
from app.models import PersonModel, User
from app.pagination import PaginatedResults
from app.schemas import PersonCreate, PersonUpdate, PersonSchema
from app.security import get_current_user


router = APIRouter(
    prefix="/api/people",  
    tags=["people"],   
)


# Get a list of people
@router.get("/", response_model=PaginatedResults[PersonSchema])
async def get_people_list(offset: int = 0, limit: int = 100, sortBy:Literal["name"] = "name", sortDescending: bool = False, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    #sort
    sort = PersonModel.name.asc()
    if sortBy == "name":
        if sortDescending:
            sort = PersonModel.name.desc()
    
    items_stmt = select(PersonModel).offset(offset).limit(limit).order_by(sort)
    person_list = db.execute(items_stmt).scalars().all()

    count_stmt = select(func.count()).select_from(PersonModel)
    total_count = db.execute(count_stmt).scalar()
    
    paginated_response = PaginatedResults[PersonSchema](
        items=person_list,
        total_count=total_count,
        offset=offset,
        limit=limit
    )
    
    return paginated_response

@router.post("/new", response_model=PersonSchema)
def add_person(person: PersonCreate, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    db_person = PersonModel(name=person.name, past_names=person.past_names)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

# Update the person record
@router.patch("/{person_id}", response_model=PersonSchema)
async def update_person(image_id: int, photo: PersonUpdate,  db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    # should restrict this to admins?
    db_person = db.query(PersonModel).filter(PersonModel.id == image_id).first()
    if db_person is None:
        raise HTTPException(status_code=404, detail="Item not found")
    update_data_in_db(db_person, photo)
    db.commit()
    db.refresh(db_person)
    return db_person