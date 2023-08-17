import os
import unittest
from parameterized import parameterized
from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from inventory_manager import InventoryManager, OrderQuantityExceedsAgreementException, \
    PurchaseOrderDateOutsideAgreementDuration, PurchaseOrderDeliveryOutsideAgreementDuration
from models.database import Base
from models.plant import Plant
from models.vendor import Vendor


class InventoryManagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.plant = Plant(name='Plant A')
        self.vendor = Vendor(name='Vendor A')

        self.engine = create_engine('sqlite:///inventory_test.db')
        # Create tables in the database
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.session.add_all([self.plant, self.vendor])
        self.session.commit()

        self.inventory_manager = InventoryManager(self.session)

    def tearDown(self) -> None:
        self.session.close_all()
        self.engine.dispose()

        db_file = "inventory_test.db"
        if os.path.exists(db_file):
            os.remove(db_file)

    def test_get_oldest_received_plant(self):
        agreement = self.inventory_manager.create_purchase_agreement(
            plant_id=self.plant.plant_id, vendor_id=self.vendor.vendor_id,
            start=date.today() - timedelta(days=35), end=date.today() + timedelta(days=365), quantity=1000
        )
        order_1 = self.inventory_manager.create_purchase_order(
            quantity=100, order_date=date.today() - timedelta(days=5), agreement_id=agreement.agreement_id
        )
        self.inventory_manager.receive_purchase_order(
            order_1.order_id, delivery_date=date.today() - timedelta(days=5)
        )

        # oldest received plant
        order_2 = self.inventory_manager.create_purchase_order(
            quantity=100, order_date=date.today() - timedelta(days=10), agreement_id=agreement.agreement_id
        )
        self.inventory_manager.receive_purchase_order(
            order_2.order_id, delivery_date=date.today() - timedelta(days=10)
        )

        order_3 = self.inventory_manager.create_purchase_order(
            quantity=100, order_date=date.today() - timedelta(days=2), agreement_id=agreement.agreement_id
        )
        self.inventory_manager.receive_purchase_order(
            order_3.order_id, delivery_date=date.today() - timedelta(days=2)
        )

        order = self.inventory_manager.get_earliest_plant_order(self.plant.plant_id)

        self.assertEqual(order.order_id, order_2.order_id)

        # now add a standalone order that is oldest delivered
        # we need to provide both vendor id and plant id for standalone orders
        order_4 = self.inventory_manager.create_purchase_order(
            quantity=100, order_date=date.today() - timedelta(days=20), vendor_id=self.vendor.vendor_id,
            plant_id=self.plant.plant_id
        )
        self.inventory_manager.receive_purchase_order(
            order_4.order_id, delivery_date=date.today() - timedelta(days=20)
        )

        order = self.inventory_manager.get_earliest_plant_order(self.plant.plant_id)
        self.assertEqual(order.order_id, order_4.order_id)

    def test_order_quantities_against_parent_agreement_quantity(self):
        agreement = self.inventory_manager.create_purchase_agreement(
            plant_id=self.plant.plant_id, vendor_id=self.vendor.vendor_id,
            start=date.today() - timedelta(days=35), end=date.today() + timedelta(days=365), quantity=150
        )
        order_1 = self.inventory_manager.create_purchase_order(
            quantity=100, order_date=date.today() - timedelta(days=5), agreement_id=agreement.agreement_id
        )
        self.inventory_manager.receive_purchase_order(
            order_1.order_id, delivery_date=date.today() - timedelta(days=5)
        )

        with self.assertRaises(OrderQuantityExceedsAgreementException):
            self.inventory_manager.create_purchase_order(
                quantity=100, order_date=date.today() - timedelta(days=10), agreement_id=agreement.agreement_id
            )

        # No issues while ordering remaining 50 plants
        self.inventory_manager.create_purchase_order(
            quantity=50, order_date=date.today() - timedelta(days=10), agreement_id=agreement.agreement_id
        )

    @parameterized.expand([
        # [(order_date, delivery_date, raises_order_date, raises_delivery_date)]
        (date.today(), date.today(), False, False),
        (date.today(), date.today() + timedelta(days=100), False, False),
        (date.today(), date.today() + timedelta(days=365), False, False),
        (date.today(), date.today() + timedelta(days=366), False, True),
        (date.today() - timedelta(days=1), date.today() + timedelta(days=1), True, False),
    ])
    def test_order_and_delivery_dates_wrt_agreement_duration(
            self, order_date, delivery_date, raises_order_date, raises_delivery_date
    ):
        agreement_start, agreement_end = date.today(), date.today() + timedelta(days=365)
        agreement = self.inventory_manager.create_purchase_agreement(
            plant_id=self.plant.plant_id, vendor_id=self.vendor.vendor_id,
            start=agreement_start, end=agreement_end, quantity=150
        )
        order_1 = None
        if raises_order_date:
            with self.assertRaises(PurchaseOrderDateOutsideAgreementDuration):
                order_1 = self.inventory_manager.create_purchase_order(
                    quantity=100, order_date=order_date, agreement_id=agreement.agreement_id
                )
        else:
            order_1 = self.inventory_manager.create_purchase_order(
                quantity=100, order_date=order_date, agreement_id=agreement.agreement_id
            )
        if order_1:
            if raises_delivery_date:
                with self.assertRaises(PurchaseOrderDeliveryOutsideAgreementDuration):
                    self.inventory_manager.receive_purchase_order(order_1.order_id, delivery_date=delivery_date)
            else:
                self.inventory_manager.receive_purchase_order(order_1.order_id, delivery_date=delivery_date)


if __name__ == '__main__':
    unittest.main()
