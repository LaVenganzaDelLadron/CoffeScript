from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import admin

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(admin.Admin).filter(admin.Admin.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = admin.Admin(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.AID}


@router.post("/login/")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(admin.Admin).filter(admin.Admin.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": db_user.AID}
