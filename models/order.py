from sqlalchemy import Column, Integer, String, Text, LargeBinary, DECIMAL, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum



class OrderTypeStatus(enum.Enum):
    pickup = "pickup"
    delivery = "delivery"

class OrderStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    preparing = "preparing"
    ready = "ready"
    completed = "completed"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(Integer)
    store_id = Column(Integer)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    order_type = Column(Enum(OrderTypeStatus), default=OrderTypeStatus.pickup)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)