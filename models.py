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

class StoreStatus(enum.Enum):
    open = "open"
    closed = "closed"

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

class CartStatus(enum.Enum):
    small = "small"
    medium = "medium"
    large = "large"


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


class AddStore(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    address = Column(String(255))
    prep_time_minutes = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(StoreStatus), default=StoreStatus.open)


class Order(Base):
    __tablename__ = "orders"
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(Integer)
    store_id = Column(Integer)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    order_type = Column(Enum(OrderTypeStatus), default=OrderTypeStatus.pickup)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)


class OrderItems(Base):
    __tablename__ = "order_items"
    id = Column(String(50), primary_key=True, index=True)
    order_id = Column(Integer)
    coffee_id = Column(Integer)
    size = Column(Enum(CartStatus), default=CartStatus.small)
    quantity = Column(DECIMAL(10, 2), nullable=False)


class Cart(Base):
    __tablename__ = "cart_items"
    id = Column(String(50), primary_key=True, index=True)
    firebase_uid = Column(String(255))
    coffee_id = Column(String(50))
    size = Column(Enum(CartStatus), default=CartStatus.small)
    quantity = Column(DECIMAL(10, 2), nullable=False)