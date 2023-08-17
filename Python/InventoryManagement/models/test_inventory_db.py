import atexit
import os
from datetime import date

from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from inventory_manager import InventoryManager
from models.database import Base
from models.plant import Plant
from models.vendor import Vendor
from models.order import Order

app = Flask(__name__)

# Create the database connection
engine = create_engine('sqlite:///test_inventory.db', echo=True)
# Create tables in the database
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

if not session.query(Plant).filter(Plant.plant_id == 1).first():
    plant = Plant(plant_id=1, name='Plant A')
    session.add(plant)
    session.commit()

if not session.query(Vendor).filter(Vendor.vendor_id == 1).first():
    vendor = Vendor(vendor_id=1, name='Vendor A')
    session.add(vendor)
    session.commit()

order = Order(
    order_date=date.today(), quantity=100, plant_id=1
)

# order = Order(
#     agreement_id=1, vendor_id=1, order_date=date.today(), quantity=100, plant_id=1
# )
#
# order = Order(
#     agreement_id=1, vendor_id=1, order_date=date.today(), quantity=100, plant_id=1
# )

session.add(order)
session.commit()
