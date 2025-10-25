from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form, APIRouter
from typing import Annotated
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import order, orderitems, coffee



router = APIRouter(prefix="/order", tags=["Order"])

order.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/getorders/")
async def get_orders(db: Session = Depends(get_db)):
    try:
        orders = db.query(order.Order).all()

        if not orders:
            raise HTTPException(status_code=404, detail="No orders found for this admin")

        return [
            {
                "id": order.id,
                "user_id": order.user_id,
                "total_amount": order.total_amount,
                "order_type": order.order_type,
                "status": order.status
            }
            for order in orders
        ]

    except Exception as e:
        print(e)


@router.get("/getstatusorders/{status}")
async def get_orders_by_status(status: str, db: Session = Depends(get_db)):
    try:
        orders = db.query(order.Order).filter(order.Order.status == status).all()

        if not orders:
            raise HTTPException(status_code=404, detail=f"No {status} orders found")

        result = []
        for order_entry in orders:
            items = (
                db.query(orderitems.OrderItems, coffee.AddCoffee.name)
                .join(coffee.AddCoffee, orderitems.OrderItems.coffee_id == coffee.AddCoffee.id)
                .filter(orderitems.OrderItems.order_id == order_entry.id)
                .all()
            )

            item_list = [
                {
                    "coffee_name": coffee_name,
                    "size": getattr(item.OrderItems.size, "value", str(item.OrderItems.size)),
                    "quantity": float(item.OrderItems.quantity)
                }
                for item, coffee_name in items
            ]

            result.append({
                "id": order_entry.id,
                "user_id": order_entry.user_id,
                "store_id": order_entry.store_id,
                "total_amount": float(order_entry.total_amount),
                "order_type": getattr(order_entry.order_type, "value", str(order_entry.order_type)),
                "status": getattr(order_entry.status, "value", str(order_entry.status)),
                "items": item_list
            })

        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        print("ERROR in get_orders_by_status:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/ordercount/")
async def get_order_count(db: Session = Depends(get_db)):
    try:
        count = db.query(func.count(order.Order.id)).scalar()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


