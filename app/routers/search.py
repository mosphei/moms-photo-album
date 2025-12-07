
from fastapi import APIRouter, Depends
from app.security import get_current_user
from rapidfuzz import fuzz

router = APIRouter(
    prefix="/api/search",  
    tags=["search"],   
)

@router.get("/")
async def search_all(q: str,current_user=Depends(get_current_user)):
    return current_user.id

@router.get('/test')
async def get_test():
    return fuzz.ratio("this is a test", "this is a test!")