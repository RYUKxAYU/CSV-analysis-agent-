from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from core.security import hash_password, verify_password, create_access_token
from db.queries.users import get_user_by_email, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    # Check if user exists
    existing = await get_user_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed = hash_password(request.password)
    user = await create_user(request.email, hashed)
    
    # Generate token
    token = create_access_token(user["id"])
    
    return AuthResponse(
        access_token=token,
        user_id=str(user["id"]),
        email=user["email"]
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    # Get user
    user = await get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate token
    token = create_access_token(user["id"])
    
    return AuthResponse(
        access_token=token,
        user_id=str(user["id"]),
        email=user["email"]
    )