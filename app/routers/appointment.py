from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, models
from ..auth import get_current_user
from ..email_utils import send_email
from ..depends import get_db

router = APIRouter()

@router.post("/appointments")
async def book_appointment(appointment: schemas.AppointmentCreate, 
                     db: AsyncSession= Depends(get_db), current_user = Depends(get_current_user)):
    
    # existing time slot checking
    result =await db.execute(select(models.Appointment).where(models.Appointment.appointment_date
                                                    == appointment.appointment_date))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="This time slot is already booked")

    new_appointment = models.Appointment(**appointment.dict(), user_id = current_user.id)

    db.add(new_appointment)
    await db.commit()
    await db.refresh(new_appointment)
    
    return {"message": "Appointment created"}

@router.get("/appointments")
async def get_appointments(db: AsyncSession= Depends(get_db), current_user= Depends(get_current_user)):
    if current_user.role == "admin":
        result = await db.execute(select(models.Appointment))
        appointments = result.scalars().all()
    else:
        result =await db.execute(select(models.Appointment).where(models.Appointment.user_id == current_user.id))
        appointments = result.scalars().all()
    
    return appointments

@router.put("/appointments/{appointment_id}")
async def update_status(appointment_id: int, status_update: schemas.AppointmentStatusUpdate,
                  background_tasks: BackgroundTasks,
                  db: AsyncSession= Depends(get_db), current_user= Depends(get_current_user)):

    if status_update.status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin can only update the status")
        
    result = await db.execute(select(models.Appointment).where(models.Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()    
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.status = status_update.status
    await db.commit()
    await db.refresh(appointment)

    # Background tasks for email sending
    res = await db.execute(select(models.User).where(models.User.id == appointment.user_id))
    user = res.scalar_one_or_none()
    
    subject = f"Appointment {status_update.status.capitalize()}"
    body = f"Hello {user.name}, your appointment has been {status_update.status}."
    background_tasks.add_task(send_email, user.email, subject, body)

    return {"message": f"Appointment {status_update.status}"}