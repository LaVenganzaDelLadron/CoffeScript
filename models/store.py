from sqlalchemy import Column, Integer, String, Text, LargeBinary, DECIMAL, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum

class StoreStatus(enum.Enum):
    open = "open"
    closed = "closed"


class AddStore(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    address = Column(String(255))
    prep_time_minutes = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(StoreStatus), default=StoreStatus.open)