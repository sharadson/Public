from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from models.database import Base


class Vendor(Base):
    __tablename__ = 'vendor'

    vendor_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    agreements = relationship('Agreement', back_populates='vendor')
    orders = relationship('Order', back_populates='vendor')
