from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form, APIRouter
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import category, coffee

router = APIRouter(prefix="/categories", tags=["Categories"])

category.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/addcategories/")
async def add_categories(name: str = Form(...), db: Session = Depends(get_db)):
    categories = db.query(category.AddCategory).filter(category.AddCategory.name == name).first()
    if categories:
        raise HTTPException(status_code=404, detail="Category already exist")

    new_category = category.AddCategory(
        name=name
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return {
        "message": "Category Added Successfully",
        "name": new_category.name,
    }


@router.put("/updatecategories/")
async def update_categories(name: str = Form(...), db: Session = Depends(get_db)):
    try:
        categories = db.query(category.AddCategory).filter(category.AddCategory.name == name).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category does not exist")

        categories.name = name

        db.commit()
        db.refresh(categories)
        return {
            "message": "Category Updated Successfully",
            "name": categories.name
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/getcategories/")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(category.AddCategory).all()
    if not categories:
        raise HTTPException(status_code=404, detail="Category does not exist")

    return [
        {
            "id": category.id,
            "name": category.name,
        }
        for category in categories
    ]


@router.delete("/deletecategories/{id}")
async def delete_category(id: int, db: Session = Depends(get_db)):
    try:
        categories = db.query(category.AddCategory).filter(category.AddCategory.id == id).first()

        if not categories:
            raise HTTPException(status_code=404, detail="Category does not exist")

        db.delete(categories)
        db.commit()

        return {"message": f"Coffee '{categories.name}' deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

