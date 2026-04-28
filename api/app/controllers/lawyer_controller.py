from fastapi import HTTPException
from typing import Optional
from app.core.database import get_db

async def search_lawyers(specialization: Optional[str] = None, location: Optional[str] = None, min_experience: Optional[int] = None):
    db = get_db()
    query = {"user_type": "lawyer"}
    
    if specialization:
        query["specialization"] = {"$regex": specialization, "$options": "i"}
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if min_experience:
        query["years_of_experience"] = {"$gte": min_experience}
    
    lawyers = await db.users.find(query).sort("rating", -1).to_list(100)
    
    for lawyer in lawyers:
        lawyer.pop('_id', None)
        lawyer.pop('password_hash', None)
    
    return lawyers

async def get_lawyer_profile(lawyer_id: str):
    db = get_db()
    lawyer = await db.users.find_one({"id": lawyer_id, "user_type": "lawyer"})
    
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    lawyer.pop('_id', None)
    lawyer.pop('password_hash', None)
    
    return lawyer
