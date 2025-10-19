from sqlalchemy import Column, Integer, String, Text, LargeBinary, DECIMAL, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum

class CartStatus(enum.Enum):
    small = "small"
    medium = "medium"
    large = "large"

class OrderItems(Base):
    __tablename__ = "order_items"
    id = Column(String(50), primary_key=True, index=True)
    order_id = Column(Integer)
    coffee_id = Column(Integer)
    size = Column(Enum(CartStatus), default=CartStatus.small)
    quantity = Column(DECIMAL(10, 2), nullable=False)