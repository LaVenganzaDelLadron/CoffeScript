import uuid
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from models import CoffeeStatus

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


@app.post("/addcoffee/")
async def add_coffee(
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    aid: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    db_coffee = db.query(models.AddCoffee).filter(models.AddCoffee.name == name).first()
    if db_coffee:
        raise HTTPException(status_code=400, detail="Coffee already exists")

    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()

    result = db.execute(text("SELECT GenerateCoffeeID()")).scalar()
    new_id = result

    new_coffee = models.AddCoffee(
        id=new_id,
        name=name,
        description=description,
        category=category,
        price=price,
        aid=aid,
        image=contents
    )

    db.add(new_coffee)
    db.commit()
    db.refresh(new_coffee)

    return {
        "message": "Coffee Added Successfully",
        "coffee_id": new_coffee.id,
        "name": new_coffee.name,
        "category": new_coffee.category
    }

