from datetime import date

from models.agreement import Agreement
from models.order import Order

"""
In practice, would like to implement this class as following
1. A gRPC based Inventory Management Service with InventoryManager methods as microservice endpoints.
2. Flask REST handlers in app.py will call the gRPC endpoints via Request/Response designed in protobuf file
3. Request/responses will be predefined/staically typed in proto file and used by both REST handlers and gRPC endpoints
 to communicate
4. Details of errors (currently raised in methods below) from gRPC endpoints will be set in the gRPC context so that
 REST handlers can except/catch them appropriately   
"""


class InventoryManager:

    def __init__(self, session):
        self.session = session

    def create_purchase_agreement(self, plant_id, vendor_id, start, end, quantity) -> Agreement:
        agreement = Agreement(
            plant_id=plant_id, vendor_id=vendor_id, agreement_date=date.today(),
            agreement_start=start, agreement_end=end, quantity=quantity
        )
        self.session.add(agreement)
        self.session.commit()
        return agreement

    def create_purchase_order(
            self, quantity, order_date=date.today(), agreement_id=None, vendor_id=None, plant_id=None
    ) -> Order:
        if not agreement_id and not vendor_id:
            raise PurchaseOrderValidationException('Either agreement_id or vendor_id needs to be provided')

        if agreement_id and vendor_id and not self._validate_agreement(agreement_id, vendor_id):
            raise PurchaseOrderValidationException(
                f'There is no agreement {agreement_id} exists for given vendor {vendor_id}'
            )

        if not agreement_id and (not vendor_id or not plant_id):
            raise PurchaseOrderValidationException(
                'If no agreement_id is given, both vendor_id and plant_id need to be provided for standalone order'
            )

        if agreement_id:
            agreement = self.session.query(Agreement).filter(Agreement.agreement_id == agreement_id).first()
            existing_quantity = sum([order.quantity for order in agreement.orders])
            if existing_quantity + quantity > agreement.quantity:
                raise OrderQuantityExceedsAgreementException(
                    f'(order quantity) {quantity} + (existing quantity) {existing_quantity} exceeds agreement quantity'
                    f'{agreement.quantity}'
                )

            if order_date < agreement.agreement_start or order_date > agreement.agreement_end:
                raise PurchaseOrderDateOutsideAgreementDuration(
                    f'order date {order_date} can not be outside of agreement duration '
                    f'{agreement.agreement_start} - {agreement.agreement_end}'
                )

        order = Order(
            agreement_id=agreement_id, vendor_id=vendor_id, order_date=order_date, quantity=quantity, plant_id=plant_id
        )
        order.agreement_id = agreement_id
        order.vendor_id = vendor_id

        self.session.add(order)
        self.session.commit()

        return order

    def receive_purchase_order(self, order_id, delivery_date=date.today()) -> Order:
        order = self.session.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            PurchaseOrderValidationException(f'order can not be found for order id {order_id}')

        if order and order.order_date > delivery_date:
            raise PurchaseOrderValidationException(
                f'delivery date {delivery_date} can not be before order date {order.order_date}'
            )

        agreement = order.agreement
        if agreement and (delivery_date < agreement.agreement_start or delivery_date > agreement.agreement_end):
            raise PurchaseOrderDeliveryOutsideAgreementDuration(
                f'order delivery date {delivery_date} can not be outside of agreement duration '
                f'{agreement.agreement_start} - {agreement.agreement_end}'
            )

        order.delivery_date = delivery_date
        self.session.commit()
        return order

    def get_purchase_agreement(self, agreement_id: int) -> Agreement:
        agreement = self.session.query(Agreement).filter(Agreement.agreement_id == agreement_id).first()
        if not agreement:
            raise PurchaseAgreementNotFound(f'Can not find purchase agreement for agreement id {agreement_id}')
        return agreement

    def get_purchase_order(self, order_id: int) -> Order:
        order = self.session.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise PurchaseOrderNotFound(f'Can not find purchase order for order id {order_id}')
        return order

    def get_earliest_plant_order(self, plant_id: int) -> Order:
        """
        Given a plant id, returns earliest received order (from agreement or standalone)
        """
        pa_orders = self.session.query(Order).join(Agreement).filter(Agreement.plant_id == plant_id).filter(Order.delivery_date != None).all()
        standalone_orders = self.session.query(Order).filter(Order.plant_id == plant_id).filter(Order.delivery_date != None).all()
        orders = pa_orders + standalone_orders
        if not orders:
            raise PlantNotFoundException(f'No orders found for given plant {plant_id}')

        orders.sort(key=lambda order: order.delivery_date)
        return orders[0]

    def _validate_agreement(self, agreement_id, vendor_id):
        _agreement = self.session.query(Agreement).filter(Agreement.agreement_id == agreement_id).first()
        return _agreement.vendor_id == vendor_id


class PurchaseOrderValidationException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PlantNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class OrderQuantityExceedsAgreementException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PurchaseOrderNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PurchaseAgreementNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PurchaseOrderDateOutsideAgreementDuration(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PurchaseOrderDeliveryOutsideAgreementDuration(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
