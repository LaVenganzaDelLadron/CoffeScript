from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form, APIRouter
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import store


router = APIRouter(prefix="/store", tags=["Store"])

store.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/addstore/")
async def add_store(
        name: str = Form(...),
        address: str = Form(...),
        prep_time_minutes: int = Form(...),
        status: str = Form(...),
        db: Session = Depends(get_db)
):
    db_store = db.query(store.AddStore).filter(
        store.AddStore.name == name,
        store.AddStore.address == address
    ).first()
    if db_store:
        raise HTTPException(status_code=400, detail="Store already exists")

    # Validate status
    if status not in ["open", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    new_store = store.AddStore(
        name=name,
        address=address,
        prep_time_minutes=prep_time_minutes,
        status=status
    )

    db.add(new_store)
    db.commit()
    db.refresh(new_store)

    return {
        "message": "Store Added Successfully",
        "store_id": new_store.id,
        "name": name,
        "address": address,
        "prep_time_minutes": prep_time_minutes,
        "status": status
    }
