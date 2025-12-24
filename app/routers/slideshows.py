from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, delete, func, select
from sqlalchemy.orm import Session

from app.models import PhotoModel, Slide, Slideshow, SlideshowCountModel, User
from app.pagination import PaginatedResults
from app.security import get_current_user
from app.database import get_db
from schemas import PhotoSchema, SlideshowCreate, SlideshowSchema, SlideshowUpdate

router = APIRouter(prefix="/api/slideshows", tags=["slideshows"])

from sqlalchemy.orm import Session


@router.get("/", response_model=PaginatedResults[SlideshowSchema])
async def get_slideshow_list(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(SlideshowCountModel)
        .where(SlideshowCountModel.user_id == current_user.id)
        .order_by(SlideshowCountModel.title)
        .offset(offset)
        .limit(limit)
    )
    slideshow_list = db.execute(query).scalars().all()
    print(slideshow_list)
    count_stmt = (
        select(func.count())
        .select_from(Slideshow)
        .where(Slideshow.user_id == current_user.id)
    )
    total_count = db.execute(count_stmt).scalar()
    return PaginatedResults[SlideshowSchema](
        items=slideshow_list, total_count=total_count, offset=offset, limit=limit
    )


def save_slides(slideshow_id: int, photo_ids: List[int], session: Session):
    # delete slides
    stmt = delete(Slide).where(Slide.slideshow_id == slideshow_id)
    session.execute(stmt)
    # now add them back again
    for idx, photo_id in enumerate(photo_ids):
        slide = Slide(slideshow_id=slideshow_id, photo_id=photo_id, order=idx)
        session.add(slide)


@router.post("/", response_model=SlideshowSchema)
async def add_slideshow(
    slideshow: SlideshowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_slideshow = Slideshow(title=slideshow.title, user_id=current_user.id)
    db.add(db_slideshow)
    db.commit()
    db.refresh(db_slideshow)
    if slideshow.slides is not None:
        save_slides(db_slideshow.id, slideshow.slides, db)
    db.commit()
    result = db.execute(
        select(SlideshowCountModel).where(SlideshowCountModel.id == db_slideshow.id)
    ).scalar()
    return result


@router.patch("/{slideshow_id}", response_model=SlideshowSchema)
async def update_slideshow(
    slideshow_id: int,
    update_slideshow: SlideshowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_slideshow = db.execute(
        select(Slideshow).where(
            and_(Slideshow.id == slideshow_id, Slideshow.user_id == current_user.id)
        )
    ).scalar()
    if db_slideshow is None:
        raise HTTPException(
            status_code=404, detail=f"slideshow '{slideshow_id}' does not exist"
        )
    db_slideshow.title = update_slideshow.title

    if update_slideshow.slides is not None:
        save_slides(slideshow_id, update_slideshow.slides, db)
    db.commit()
    # get it bck
    db_slideshow = db.execute(
        select(SlideshowCountModel).where(SlideshowCountModel.id == slideshow_id)
    ).scalar()
    return db_slideshow
