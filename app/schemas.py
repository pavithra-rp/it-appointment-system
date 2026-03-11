from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class AppointmentCreate(BaseModel):
    title: str
    description: str
    team: str
    appointment_date: datetime

class AppointmentStatusUpdate(BaseModel):
    status: str