import atexit
import os
from datetime import datetime

from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from inventory_manager import InventoryManager
from models.database import Base
from models.plant import Plant
from models.vendor import Vendor

app = Flask(__name__)

# Create the database connection
engine = create_engine('sqlite:///inventory.db', echo=True)
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

inventory_manager = InventoryManager(session)


@app.route('/create_purchase_agreement', methods=['POST'])
def create_purchase_agreement():
    data = request.json
    plant_id = int(data['plant_id'])
    vendor_id = int(data['vendor_id'])
    start_date = datetime.strptime(data['start'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end'], '%Y-%m-%d').date()
    quantity = int(data['quantity'])
    agreement = inventory_manager.create_purchase_agreement(
        plant_id=plant_id, vendor_id=vendor_id, start=start_date, end=end_date, quantity=quantity
    )
    return jsonify(agreement.serialize()), 201


@app.route('/create_purchase_order', methods=['POST'])
def create_purchase_order():
    data = request.json
    agreement_id = int(data['agreement_id']) if 'agreement_id' in data else None
    vendor_id = int(data['vendor_id']) if 'vendor_id' in data else None
    plant_id = int(data['plant_id'])
    order_date = datetime.strptime(data['order_date'], '%Y-%m-%d').date()
    quantity = int(data['quantity'])
    order = inventory_manager.create_purchase_order(
        agreement_id=agreement_id, order_date=order_date, vendor_id=vendor_id, plant_id=plant_id, quantity=quantity
    )
    return jsonify(order.serialize()), 201


@app.route('/receive_purchase_order', methods=['POST'])
def receive_purchase_order():
    data = request.json
    order_id = int(data['order_id'])
    delivery_date = datetime.strptime(data['delivery_date'], '%Y-%m-%d').date()
    order = inventory_manager.receive_purchase_order(order_id=order_id, delivery_date=delivery_date)
    return jsonify(order.serialize()), 201


@app.route('/get_purchase_agreement', methods=['POST'])
def get_purchase_agreement():
    data = request.json
    agreement_id = int(data['agreement_id'])
    agreement = inventory_manager.get_purchase_agreement(agreement_id)
    if agreement:
        return jsonify(agreement.serialize()), 200
    else:
        return f'Agreement not found for agreement_id: {agreement_id}', 404


@app.route('/get_purchase_order', methods=['POST'])
def get_purchase_order():
    data = request.json
    order_id = int(data['order_id']) if 'order_id' in data else None
    plant_id = int(data['plant_id']) if 'plant_id' in data else None
    order = None
    if order_id:
        order = inventory_manager.get_purchase_order(order_id)
    else:
        if plant_id:
            order = inventory_manager.get_earliest_plant_order(plant_id)
    if order:
        return jsonify(order.serialize()), 200
    else:
        return f'Order not found for order_id: {order_id} or plant_id: {plant_id}', 404


def cleanup():
    session.close_all()
    engine.dispose()

    db_file = "inventory.db"
    if os.path.exists(db_file):
        os.remove(db_file)


atexit.register(cleanup)

if __name__ == '__main__':
    app.run()
