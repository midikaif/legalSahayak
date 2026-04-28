from fastapi import APIRouter
from app.controllers import auth_controller
from app.schemas.user import UserCreate, UserLogin, Token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    return await auth_controller.register_user(user_data)

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    return await auth_controller.login_user(user_data)
