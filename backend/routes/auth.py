from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.session import get_db
from models.user import User
from schemas.auth import Token, UserCreate, UserLogin, UserResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account (role defaults to user)."""
    return AuthService.register_user(db, user_data)


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return a JWT access token."""
    user = AuthService.authenticate_user(db, credentials)
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value}
    )
    return Token(access_token=access_token)


@router.post("/token", response_model=Token, include_in_schema=False)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2-compatible token endpoint for Swagger UI authorization."""
    credentials = UserLogin(username=form_data.username, password=form_data.password)
    user = AuthService.authenticate_user(db, credentials)
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value}
    )
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
