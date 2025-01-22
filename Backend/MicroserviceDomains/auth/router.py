from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import schemas, service
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_service = service.UserService(db)
    return user_service.create_user(user)
