
from fastapi import APIRouter, Depends, HTTPException

from app.models import SlideShow, User
from app.security import get_current_user
router = APIRouter(prefix='/api/slideshows', tags=['slideshows'])
from app.database import get_db
from schemas import SlideshowCreate, SlideshowSchema

from sqlalchemy.orm import Session

@router.post("/new", response_model=SlideshowSchema)
def add_person(
    slideshow: SlideshowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_slideshow = SlideShow(title=slideshow.title, user=current_user, slides=slideshow.slides)
    db.add(db_slideshow)
    db.commit()
    db.refresh(db_slideshow)
    return db_slideshow