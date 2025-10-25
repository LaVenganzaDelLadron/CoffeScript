from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form, APIRouter
from typing import Annotated
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import admin, order


router = APIRouter(prefix="/money", tags=["Money"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/totalrevenue/")
async def get_total_revenue(db: Session = Depends(get_db)):
    try:
        total = db.query(func.sum(order.Order.total_amount)) \
            .filter(order.Order.status == 'completed') \
            .scalar()
        total_revenue = float(total or 0.0)
        return {"total_revenue": total_revenue}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pendingpayments/")
async def get_pending_revenue(db: Session = Depends(get_db)):
    try:
        pending_orders = db.query(order.Order) \
            .filter(order.Order.status == 'pending') \
            .all()
        total_pending = sum(float(order.total_amount) for order in pending_orders)
        return {"pending_revenue": total_pending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



