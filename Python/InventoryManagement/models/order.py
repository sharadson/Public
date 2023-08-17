from sqlalchemy import CheckConstraint
from sqlalchemy import Column, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.database import Base


class Order(Base):
    __tablename__ = 'order'

    def __eq__(self, other):
        if isinstance(other, Order):
            return self.order_id == other.order_id
        return False

    def __hash__(self):
        return hash(self.order_id)

    # constraints on certain columns
    __table_args__ = (
        CheckConstraint(
            # Both agreement_id and vendor_id cannot be null at the same time
            "(agreement_id IS NOT NULL OR vendor_id IS NOT NULL)",
            name="agreement_vendor_not_both_null"
        ),
        CheckConstraint(
            # when agreement_id is NULL and vendor_id is NOT NULL, plant_id needs to be populated
            "(agreement_id IS NULL AND vendor_id IS NOT NULL AND plant_id IS NOT NULL) OR (agreement_id IS NOT NULL)",
            name="agreement_vendor_plant_check"
        )
    )

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    # we can define these constraints depending on business needs: onupdate="CASCADE", ondelete="CASCADE"
    # which means what we want to do when the parent record of agreement is updated or deleted
    agreement_id = Column(Integer, ForeignKey('agreement.agreement_id'))
    vendor_id = Column(Integer, ForeignKey('vendor.vendor_id'))
    plant_id = Column(Integer, ForeignKey('plant.plant_id'))
    order_date = Column(Date, nullable=False)
    delivery_date = Column(Date)
    quantity = Column(Integer, nullable=False)
    agreement = relationship('Agreement', back_populates='orders')
    vendor = relationship('Vendor', back_populates='orders')

    def serialize(self):
        return {
            'order_id': self.order_id,
            'agreement_id': self.agreement_id,
            'vendor_id': self.vendor_id,
            'plant_id': self.plant_id,
            'order_date': self.order_date.strftime('%Y-%m-%d'),
            'delivery_date': self.delivery_date.strftime('%Y-%m-%d') if self.delivery_date else None,
            'quantity': self.quantity
        }
