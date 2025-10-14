import uuid
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy import text, func
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




@app.post("/addstore/")
async def add_store(
        name: str = Form(...),
        address: str = Form(...),
        prep_time_minutes: int = Form(...),
        status: str = Form(...),
        db: Session = Depends(get_db)
):
    db_store = db.query(models.AddStore).filter(
        models.AddStore.name == name,
        models.AddStore.address == address
    ).first()
    if db_store:
        raise HTTPException(status_code=400, detail="Store already exists")

    # Validate status
    if status not in ["open", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    new_store = models.AddStore(
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




@app.delete("/deletecoffee/{coffee_id}", status_code=status.HTTP_200_OK)
async def delete_coffee(coffee_id: str, db: Session = Depends(get_db)):
    try:
        coffee = db.query(models.AddCoffee).filter(models.AddCoffee.id == coffee_id).first()

        if not coffee:
            raise HTTPException(status_code=404, detail="Coffee not found")

        db.delete(coffee)
        db.commit()

        return {"message": f"Coffee '{coffee.name}' deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.put("/updatecoffee/{coffee_id}", status_code=status.HTTP_200_OK)
async def update_coffee(
    coffee_id: str,
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    aid: int = Form(...),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    try:
        coffee = db.query(models.AddCoffee).filter(models.AddCoffee.id == coffee_id).first()
        if not coffee:
            raise HTTPException(status_code=404, detail="Coffee not found")

        coffee.name = name
        coffee.description = description
        coffee.category = category
        coffee.price = price
        coffee.aid = aid

        if file is not None:
            contents = await file.read()
            coffee.image = contents

        db.commit()
        db.refresh(coffee)

        return {
            "message": f"Coffee '{coffee.name}' updated successfully!",
            "coffee_id": coffee.id,
            "name": coffee.name,
            "category": coffee.category,
            "price": float(coffee.price)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/getproducts/{aid}")
async def get_products(aid: int, db: Session = Depends(get_db)):
    products = db.query(models.AddCoffee).filter(models.AddCoffee.aid == aid).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found for this admin")

    return [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "price": float(product.price),
            "aid": product.aid
        }
        for product in products
    ]



@app.get("/getstatusorders/{status}")
async def get_orders_by_status(status: str, db: Session = Depends(get_db)):
    try:
        orders = db.query(models.Order).filter(models.Order.status == status).all()

        if not orders:
            raise HTTPException(status_code=404, detail=f"No {status} orders found")

        result = []
        for order in orders:
            items = (
                db.query(models.OrderItems, models.AddCoffee.name)
                .join(models.AddCoffee, models.OrderItems.coffee_id == models.AddCoffee.id)
                .filter(models.OrderItems.order_id == order.id)
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
                "id": order.id,
                "user_id": order.user_id,
                "store_id": order.store_id,
                "total_amount": float(order.total_amount),
                "order_type": getattr(order.order_type, "value", str(order.order_type)),
                "status": getattr(order.status, "value", str(order.status)),
                "items": item_list
            })

        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        print("🚨 ERROR in get_orders_by_status:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")






@app.get("/productcount/{aid}")
async def get_product_count(aid: int, db: Session = Depends(get_db)):
    try:
        count = db.query(models.AddCoffee).filter(models.AddCoffee.aid == aid).count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/ordercount/")
async def get_order_count(db: Session = Depends(get_db)):
    try:
        count = db.query(func.count(models.Order.id)).scalar()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/getorders/")
async def get_products(db: Session = Depends(get_db)):
    try:
        orders = db.query(models.Order).all()

        if not orders:
            raise HTTPException(status_code=404, detail="No orders found for this admin")

        return [
            {
                "id": order.id,
                "user_id": order.user_id,
                "store_id": order.store_id,
                "total_amount": order.total_amount,
                "order_type": order.order_type,
                "status": order.status
            }
            for order in orders
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/getcartitems/")
async def get_cartitems(db: Session = Depends(get_db)):
    try:
        carts = db.query(models.Cart).all()

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


@app.get("/totalrevenue/")
async def get_total_revenue(db: Session = Depends(get_db)):
    try:
        total = db.query(func.sum(models.Order.total_amount))\
                  .filter(models.Order.status == 'completed')\
                  .scalar()
        total_revenue = float(total or 0.0)
        return {"total_revenue": total_revenue}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/pendingpayments/")
async def get_pending_revenue(db: Session = Depends(get_db)):
    try:
        pending_orders = db.query(models.Order)\
                           .filter(models.Order.status == 'pending')\
                           .all()
        total_pending = sum(float(order.total_amount) for order in pending_orders)
        return {"pending_revenue": total_pending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

