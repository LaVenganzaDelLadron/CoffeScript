from sqlalchemy import Column, Integer, String, Text, LargeBinary, DECIMAL, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum


class AddCategory(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

