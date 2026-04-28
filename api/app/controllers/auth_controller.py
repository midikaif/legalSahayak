from fastapi import HTTPException
from app.schemas.user import UserCreate, UserLogin, User
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token

async def register_user(user_data: UserCreate):
    db = get_db()
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user_data.dict()
    password = user_dict.pop('password')
    user_dict['password_hash'] = get_password_hash(password)
    
    user = User(**user_dict)
    await db.users.insert_one(user.dict())
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    
    user_response = user.dict()
    user_response.pop('password_hash')
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

async def login_user(user_data: UserLogin):
    db = get_db()
    user = await db.users.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user['email'], "user_id": user['id']})
    
    user.pop('password_hash')
    user.pop('_id', None)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
