from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import cart



router = APIRouter(prefix="/cart", tags=["Cart"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/getcartitems/")
async def get_cart_items(db: Session = Depends(get_db)):
    try:
        carts = db.query(cart.Cart).all()

        if not carts:
            raise HTTPException(status_code=404, detail="No cart found for this admin")

        return [
            {
                "id": cart.id,
                "firebase_uid": cart.firebase_uid,
                "coffee_id": cart.coffee_id,
                "size": cart.size,
                "quantity": cart.quantity
            }
            for cart in carts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))