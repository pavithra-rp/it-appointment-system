from fastapi import APIRouter, Depends, HTTPException, Response
from .. import models, schemas
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth import create_token
from ..depends import get_db
from ..utils import hash_password, verify_password

router= APIRouter()

@router.post("/register")
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    data = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_user = data.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Already user exists.")
    
    hashed_pw = hash_password(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        role=user.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "User registered successfully."}

@router.post("/login")
async def login(data: schemas.UserLogin,response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token({"user_id": user.id})

    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")

    return {"message": "Login successful", "access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):

    response.delete_cookie("access_token")

    return {"message": "Logged out"}