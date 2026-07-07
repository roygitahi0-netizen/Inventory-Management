import os
import tempfile
import unittest

from models import InventoryRepository, init_db


class TestInventoryRepository(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        init_db(self.db_path)
        self.repo = InventoryRepository(self.db_path)

    def tearDown(self):
        os.remove(self.db_path)

    def test_create_item(self):
        item = self.repo.create_item(name="Widget", quantity=10, price=2.5)
        self.assertIsNotNone(item["id"])
        self.assertEqual(item["name"], "Widget")
        self.assertEqual(item["quantity"], 10)
        self.assertEqual(item["price"], 2.5)

    def test_create_item_requires_name(self):
        with self.assertRaises(ValueError):
            self.repo.create_item(name="")

    def test_get_all_items(self):
        self.repo.create_item(name="A", quantity=1)
        self.repo.create_item(name="B", quantity=2)
        items = self.repo.get_all_items()
        self.assertEqual(len(items), 2)

    def test_get_all_items_filter_by_category(self):
        self.repo.create_item(name="Apple", category="Produce")
        self.repo.create_item(name="Bread", category="Bakery")
        items = self.repo.get_all_items(category="Produce")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "Apple")

    def test_get_all_items_low_stock(self):
        self.repo.create_item(name="Low", quantity=1)
        self.repo.create_item(name="High", quantity=50)
        items = self.repo.get_all_items(low_stock_threshold=5)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "Low")

    def test_get_item(self):
        created = self.repo.create_item(name="Widget")
        fetched = self.repo.get_item(created["id"])
        self.assertEqual(fetched["name"], "Widget")

    def test_get_item_not_found(self):
        self.assertIsNone(self.repo.get_item(9999))

    def test_search_by_name(self):
        self.repo.create_item(name="Chocolate Bar")
        self.repo.create_item(name="Granola Bar")
        self.repo.create_item(name="Milk")
        results = self.repo.search_by_name("Bar")
        self.assertEqual(len(results), 2)

    def test_get_by_barcode(self):
        self.repo.create_item(name="Widget", barcode="12345")
        found = self.repo.get_by_barcode("12345")
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "Widget")

    def test_update_item(self):
        created = self.repo.create_item(name="Widget", quantity=5)
        updated = self.repo.update_item(created["id"], quantity=20, price=9.99)
        self.assertEqual(updated["quantity"], 20)
        self.assertEqual(updated["price"], 9.99)
        self.assertEqual(updated["name"], "Widget")  # unchanged

    def test_update_item_not_found(self):
        result = self.repo.update_item(9999, quantity=5)
        self.assertIsNone(result)

    def test_delete_item(self):
        created = self.repo.create_item(name="Widget")
        deleted = self.repo.delete_item(created["id"])
        self.assertTrue(deleted)
        self.assertIsNone(self.repo.get_item(created["id"]))

    def test_delete_item_not_found(self):
        self.assertFalse(self.repo.delete_item(9999))


if __name__ == "__main__":
    unittest.main()