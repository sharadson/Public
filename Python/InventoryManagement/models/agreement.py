from sqlalchemy import Column, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.database import Base


class Agreement(Base):
    __tablename__ = 'agreement'

    agreement_id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('plant.plant_id'), nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendor.vendor_id'), nullable=False)
    agreement_date = Column(Date)
    agreement_start = Column(Date)
    agreement_end = Column(Date)
    quantity = Column(Integer, nullable=False)
    orders = relationship('Order', back_populates='agreement')
    # we skip to back populate agreements on plant there can be too many agreements for a given plant
    plant = relationship('Plant')
    vendor = relationship('Vendor', back_populates='agreements')

    def serialize(self):
        return {
            'agreement_id': self.agreement_id,
            'plant_id': self.plant_id,
            'vendor_id': self.vendor_id,
            'agreement_date': self.agreement_date.strftime('%Y-%m-%d'),
            'agreement_start': self.agreement_start.strftime('%Y-%m-%d'),
            'agreement_end': self.agreement_end.strftime('%Y-%m-%d'),
            'quantity': self.quantity
        }
