from fastapi import HTTPException
from app.schemas.user import UserCreate, UserLogin, User
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
import logging

logger = logging.getLogger(__name__)

async def register_user(user_data: UserCreate):
    logger.info(f"Attempting to register user: {user_data.email}")
    try:
        db = get_db()
        logger.info("Successfully fetched DB instance. Querying for existing user...")
        existing_user = await db.users.find_one({"email": user_data.email})
        
        if existing_user:
            logger.warning(f"User already exists: {user_data.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_dict = user_data.dict()
        password = user_dict.pop('password')
        user_dict['password_hash'] = get_password_hash(password)
        
        logger.info("Inserting new user into database...")
        user = User(**user_dict)
        await db.users.insert_one(user.dict())
        logger.info("User successfully inserted.")
        
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        
        user_response = user.dict()
        user_response.pop('password_hash')
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}", exc_info=True)
        raise e

async def login_user(user_data: UserLogin):
    logger.info(f"Attempting login for user: {user_data.email}")
    try:
        db = get_db()
        logger.info("Successfully fetched DB instance. Querying user...")
        user = await db.users.find_one({"email": user_data.email})
        
        if not user:
            logger.warning("User not found.")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(user_data.password, user['password_hash']):
            logger.warning("Password verification failed.")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info("Password verified. Generating token...")
        access_token = create_access_token(data={"sub": user['email'], "user_id": user['id']})
        
        user.pop('password_hash')
        user.pop('_id', None)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        raise e
