import uuid
from typing import Annotated
from sqlalchemy import text, func
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form, APIRouter
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import coffee



router = APIRouter(prefix="/coffee", tags=["Coffee"])


coffee.Base.metadata.create_all(bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/addcoffee/")
async def add_coffee(
        name: str = Form(...),
        description: str = Form(...),
        category: str = Form(...),
        price: float = Form(...),
        aid: int = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    db_coffee = db.query(coffee.AddCoffee).filter(coffee.AddCoffee.name == name).first()
    if db_coffee:
        raise HTTPException(status_code=400, detail="Coffee already exists")

    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()

    result = db.execute(text("SELECT GenerateCoffeeID()")).scalar()
    new_id = result

    new_coffee = coffee.AddCoffee(
        id=new_id,
        aid=aid,
        name=name,
        description=description,
        image=contents,
        category_id=category,
        price=price,
    )

    db.add(new_coffee)
    db.commit()
    db.refresh(new_coffee)

    return {
        "message": "Coffee Added Successfully",
        "coffee_id": new_coffee.id,
        "name": new_coffee.name,
        "category": new_coffee.category_id
    }


@router.delete("/deletecoffee/{coffee_id}", status_code=status.HTTP_200_OK)
async def delete_coffee(coffee_id: str, db: Session = Depends(get_db)):
    try:
        coffees = db.query(coffee.AddCoffee).filter(coffee.AddCoffee.id == coffee_id).first()

        if not coffees:
            raise HTTPException(status_code=404, detail="Coffee not found")

        db.delete(coffees)
        db.commit()

        return {"message": f"Coffee '{coffees.name}' deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/updatecoffee/{coffee_id}", status_code=status.HTTP_200_OK)
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
        coffees = db.query(coffee.AddCoffee).filter(coffee.AddCoffee.id == coffee_id).first()
        if not coffee:
            raise HTTPException(status_code=404, detail="Coffee not found")

        coffees.name = name
        coffees.description = description
        coffees.category = category
        coffees.price = price
        coffees.aid = aid

        if file is not None:
            contents = await file.read()
            coffee.image = contents

        db.commit()
        db.refresh(coffees)

        return {
            "message": f"Coffee '{coffees.name}' updated successfully!",
            "coffee_id": coffees.id,
            "name": coffees.name,
            "category": coffees.category,
            "price": float(coffees.price)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getproducts/{aid}")
async def get_products(aid: int, db: Session = Depends(get_db)):
    products = db.query(coffee.AddCoffee).filter(coffee.AddCoffee.aid == aid).all()

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


@router.get("/coffeecount/{aid}")
async def get_coffee_count(aid: int, db: Session = Depends(get_db)):
    try:
        count = db.query(coffee.AddCoffee).filter(coffee.AddCoffee.aid == aid).count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
