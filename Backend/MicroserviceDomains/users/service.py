from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from . import schemas
from users.service import UserService

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db_session):
        self.db = db_session
        self.user_service = UserService(db_session)

    def authenticate_user(self, username: str, password: str):
        user = self.user_service.get_user_by_username(username)
        if not user or not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
