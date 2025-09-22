from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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

db_dependency = Annotated[Session, Depends(get_db)]


@app.post("/signup/", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: db_dependency):
    db_user = db.query(models.Admin).filter(models.Admin.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.Admin(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.AID}


@app.post("/login/")
async def login(user: UserLogin, db: db_dependency):
    db_user = db.query(models.Admin).filter(models.Admin.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "Login successfully", "user_id": db_user.AID}




