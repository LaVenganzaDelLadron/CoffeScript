from sqlalchemy import Column, Integer, String, Text, LargeBinary, DECIMAL, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum




class CartStatus(enum.Enum):
    small = "small"
    medium = "medium"
    large = "large"

class Cart(Base):
    __tablename__ = "cart_items"
    id = Column(String(50), primary_key=True, index=True)
    firebase_uid = Column(String(255))
    coffee_id = Column(String(50))
    size = Column(Enum(CartStatus), default=CartStatus.small)
    quantity = Column(DECIMAL(10, 2), nullable=False)