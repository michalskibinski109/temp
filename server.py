from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Base model for user registration
class Registration(BaseModel):
    user_type: str  # Senior or Caregiver
    symptoms: Optional[bool] = None
    travel_history: Optional[str] = None
    personal_info: Optional[dict] = None

# In-memory storage of responses
registrations = {}

@app.post("/register/")
async def register(registration: Registration):
    registration_id = len(registrations) + 1
    registrations[registration_id] = registration.dict()
    return {"id": registration_id, "data": registration.dict()}

@app.get("/registration/{registration_id}")
async def get_registration(registration_id: int):
    try:
        return registrations[registration_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Registration not found")
