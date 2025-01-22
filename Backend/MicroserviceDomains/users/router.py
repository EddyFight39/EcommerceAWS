from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from . import schemas, service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    auth_service = service.AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth_service.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
