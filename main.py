from fastapi import FastAPI
from app.database import Base, engine
from app.routers import user, appointment

app = FastAPI(title="Booking Appointment")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(user.router)
app.include_router(appointment.router)

@app.get("/")
async def home():
    return {"message": "API running"}