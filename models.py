from sqlalchemy import Column, Integer, String
from database import Base

class Admin(Base):
    __tablename__ = "admin"
    AID = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


class Coffees(Base):
    __tablename__ = "coffees"

