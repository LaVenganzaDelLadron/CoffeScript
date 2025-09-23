from sqlalchemy import Column, Integer, String, Text, LargeBinary, DECIMAL, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
import enum

class Admin(Base):
    __tablename__ = "admin"
    AID = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    coffees = relationship("AddCoffee", back_populates="admin")


class CoffeeStatus(enum.Enum):
    active = "active"
    inactive = "inactive"

class AddCoffee(Base):
    __tablename__ = "coffees"
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String(255))
    category = Column(String(255))
    price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(CoffeeStatus), default=CoffeeStatus.active)
    image = Column(LargeBinary)
    aid = Column(Integer, ForeignKey("admin.AID", ondelete="CASCADE"))

    admin = relationship("Admin", back_populates="coffees")


