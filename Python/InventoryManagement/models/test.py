from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# Create the database connection
engine = create_engine('sqlite:///purchase.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Define the data models
Base = declarative_base()


class PurchaseAgreement(Base):
    __tablename__ = 'purchase_agreements'

    agreement_id = Column(Integer, primary_key=True)
    vendor = Column(String, nullable=False)
    total_quantity = Column(Integer, nullable=False)
    purchase_orders = relationship('PurchaseOrder', back_populates='agreement')


class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'

    order_id = Column(Integer, primary_key=True)
    agreement_id = Column(Integer, ForeignKey('purchase_agreements.agreement_id'))
    quantity = Column(Integer, nullable=False)
    agreement = relationship('PurchaseAgreement', back_populates='purchase_orders')


# Create tables in the database
Base.metadata.create_all(engine)

# Create a PurchaseAgreement
pa = PurchaseAgreement(vendor="Vendor A", total_quantity=100)
session.add(pa)
session.commit()

# Create PurchaseOrders and associate them with the PurchaseAgreement
po1 = PurchaseOrder(agreement=pa, quantity=20)
po2 = PurchaseOrder(agreement=pa, quantity=30)

session.add(po1)
session.add(po2)
session.commit()

# Query and print details
agreement = session.query(PurchaseAgreement).get(1)
print("Purchase Agreement:", agreement.vendor, agreement.total_quantity)
for order in agreement.purchase_orders:
    print("Purchase Order:", order.quantity)
