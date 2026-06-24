from fastapi import APIRouter, Depends, HTTPException, status

import database
import auth
from schemas import UserRegister, UserLogin, UserOut, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister):
    existing = database.get_user_by_email(payload.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    hashed = auth.hash_password(payload.password)
    new_id = database.create_user(payload.email, hashed)

    return UserOut(id=new_id, email=payload.email)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin):
    user = database.get_user_by_email(payload.email)

    if user is None or not auth.verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = auth.create_session_token(user["email"])
    return TokenResponse(access_token=token, email=user["email"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: str = Depends(auth.get_current_user)):
    user = database.get_user_by_email(current_user)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return UserOut(id=user["id"], email=user["email"])