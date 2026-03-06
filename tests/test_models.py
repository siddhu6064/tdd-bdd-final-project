# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel
"""
import os
import logging
import unittest
from decimal import Decimal

from service import app
from service.models import (
    Category,
    DataValidationError,
    Product,
    db,
    init_db,
)
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertIsNotNone(product)
        self.assertIsNone(product.id)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertTrue(product.available)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_repr(self):
        """It should return the string representation of a Product"""
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )
        self.assertEqual(repr(product), "<Product Fedora id=[None]>")

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()

        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)

        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        found_product = Product.find(product.id)
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        product.description = "testing"
        original_id = product.id
        product.update()

        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")

        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "testing")

    def test_update_with_no_id(self):
        """It should not Update a Product with no id"""
        product = ProductFactory()
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertEqual(len(Product.all()), 1)

        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])

        for _ in range(5):
            product = ProductFactory()
            product.create()

        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_does_not_exist(self):
        """It should return None if a Product is not found"""
        product = Product.find(0)
        self.assertIsNone(product)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        name = products[0].name
        count = len([product for product in products if product.name == name])

        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_price(self):
        """It should Find Products by Price"""
        product1 = ProductFactory(price=Decimal("19.95"))
        product2 = ProductFactory(price=Decimal("19.95"))
        product3 = ProductFactory(price=Decimal("29.95"))

        product1.create()
        product2.create()
        product3.create()

        found = Product.find_by_price(Decimal("19.95"))
        self.assertEqual(found.count(), 2)
        for product in found:
            self.assertEqual(product.price, Decimal("19.95"))

    def test_find_by_price_string(self):
        """It should Find Products by Price from a string"""
        product = ProductFactory(price=Decimal("39.95"))
        product.create()

        found = Product.find_by_price('"39.95"')
        self.assertEqual(found.count(), 1)
        self.assertEqual(found.first().price, Decimal("39.95"))

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        available = products[0].available
        count = len(
            [product for product in products if product.available == available]
        )

        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        category = products[0].category
        count = len([product for product in products if product.category == category])

        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_serialize_a_product(self):
        """It should serialize a Product"""
        product = Product(
            id=1,
            name="Fedora",
            description="A red hat",
            price=Decimal("12.50"),
            available=True,
            category=Category.CLOTHS,
        )
        data = product.serialize()

        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Fedora")
        self.assertEqual(data["description"], "A red hat")
        self.assertEqual(data["price"], "12.50")
        self.assertTrue(data["available"])
        self.assertEqual(data["category"], "CLOTHS")

    def test_deserialize_a_product(self):
        """It should deserialize a Product"""
        data = {
            "name": "Fedora",
            "description": "A red hat",
            "price": "12.50",
            "available": True,
            "category": "CLOTHS",
        }
        product = Product()
        product.deserialize(data)

        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.price, Decimal("12.50"))
        self.assertTrue(product.available)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_deserialize_missing_key(self):
        """It should not deserialize a Product with a missing key"""
        data = {
            "name": "Fedora",
            "price": "12.50",
            "available": True,
            "category": "CLOTHS",
        }
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, None)

    def test_deserialize_invalid_available(self):
        """It should not deserialize a Product with invalid available type"""
        data = {
            "name": "Fedora",
            "description": "A red hat",
            "price": "12.50",
            "available": "True",
            "category": "CLOTHS",
        }
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_invalid_category(self):
        """It should not deserialize a Product with invalid category"""
        data = {
            "name": "Fedora",
            "description": "A red hat",
            "price": "12.50",
            "available": True,
            "category": "BOGUS",
        }
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_model_init_db(self):
        """It should call init_db"""
        init_db(app)
        self.assertIsNotNone(db)
