from sqlalchemy import Column, Integer, String, Text, LargeBinary, DECIMAL, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum



class CoffeeStatus(enum.Enum):
    active = "active"
    inactive = "inactive"

class AddCoffee(Base):
    __tablename__ = 'coffees'
    id = Column(String(50), primary_key=True, index=True)
    aid = Column(Integer, ForeignKey("admin.AID", ondelete="CASCADE"))
    name = Column(String(50))
    description = Column(String(255))
    image = Column(LargeBinary)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'))
    price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(CoffeeStatus), default=CoffeeStatus.active)

    admin = relationship("Admin", back_populates="coffees")







