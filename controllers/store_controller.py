from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form, APIRouter
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import store, coffee

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

@router.put("/updatestore/{store_id}", status_code=status.HTTP_200_OK)
async def update_store(
    store_id: int,
    name: str = Form(...),
    address: str = Form(...),
    prep_time_minutes: int = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    store_item = db.query(store.AddStore).filter(store.AddStore.id == store_id).first()

    if not store_item:
        raise HTTPException(status_code=404, detail="Store not found")

    if status not in ["open", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    store_item.name = name
    store_item.address = address
    store_item.prep_time_minutes = prep_time_minutes
    store_item.status = status

    db.commit()
    db.refresh(store_item)

    return {
        "message": f"Store '{store_item.name}' updated successfully!",
        "store_id": store_item.id,
        "name": store_item.name,
        "address": store_item.address,
        "prep_time_minutes": store_item.prep_time_minutes,
        "status": store_item.status,
    }




@router.get("/getstores/")
async def get_stores(db: Session = Depends(get_db)):
    stores = db.query(store.AddStore).all()

    if not stores:
        raise HTTPException(status_code=404, detail="Store not found")

    return [
        {
            "id": s.id,
            "name": s.name,
            "address": s.address,
            "prep_time_minutes": str(s.prep_time_minutes),
            "status": s.status.value if s.status else None
        }
        for s in stores
    ]

@router.delete("/deletestore/{store_id}")
async def delete_store(store_id: int, db: Session = Depends(get_db)):
    try:
        stores = db.query(store.AddStore).filter(store.AddStore.id == store_id).first()

        if not stores:
            raise HTTPException(status_code=404, detail="Store not found")

        db.delete(stores)
        db.commit()

        return {"message": f"Store {stores.name} Deleted Successfully"}

    except Exception as e:
        raise HTTPException(status_code=404, detail="Store not found")