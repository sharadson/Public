from sqlalchemy import Column, Integer, String
from models.database import Base


class Plant(Base):
    __tablename__ = 'plant'

    plant_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
