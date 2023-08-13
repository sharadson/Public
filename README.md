# Inventory Management System

Welcome to the Inventory Management System project! This system allows you to manage Purchase Agreements (PA) and Purchase Orders (PO) for different plants and vendors. You can use the provided API endpoints to interact with the system.

## API Endpoints

### PA (Purchase Agreement)

#### Create PA:

curl -X POST -H "Content-Type: application/json" -d '{
  "plant_id": 1,
  "vendor_id": 1,
  "start": "2023-01-01",
  "end": "2024-01-01",
  "quantity": 1000
}' http://127.0.0.1:5000/create_purchase_agreement


#### Get PA:

curl -X POST -H "Content-Type: application/json" -d '{
  "agreement_id": 1
}' http://127.0.0.1:5000/get_purchase_agreement


### PO (Purchase Order)


#### Create PO (Standard PO):

curl -X POST -H "Content-Type: application/json" -d '{
  "plant_id": 1,
  "agreement_id": 1,
  "order_date": "2023-01-01",
  "quantity": 100
}' http://127.0.0.1:5000/create_purchase_order

#### Create PO (Standalone PO):

curl -X POST -H "Content-Type: application/json" -d '{
  "vendor_id": 1,
  "plant_id": 1,
  "order_date": "2022-01-01",
  "quantity": 100
}' http://127.0.0.1:5000/create_purchase_order


### Receive PO:

#### Receive Standard PO:

curl -X POST -H "Content-Type: application/json" -d '{
  "order_id": 1,
  "delivery_date": "2023-05-01"
}' http://127.0.0.1:5000/receive_purchase_order

#### Receive Standalone PO:

curl -X POST -H "Content-Type: application/json" -d '{
  "order_id": 2,
  "delivery_date": "2023-02-01"
}' http://127.0.0.1:5000/receive_purchase_order


### Get PO:

#### Get PO using order_id:

curl -X POST -H "Content-Type: application/json" -d '{
  "order_id": 1
}' http://127.0.0.1:5000/get_purchase_order


#### Get PO Using plant_id 
Returns earliest order for the plant which is standalone PO - which is delivered earlier - in this case!):

curl -X POST -H "Content-Type: application/json" -d '{
  "plant_id": 1
}' http://127.0.0.1:5000/get_purchase_order
