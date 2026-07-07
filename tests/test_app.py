import os
import tempfile
import unittest
from unittest.mock import patch

from app import create_app


class TestInventoryAPI(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        self.app = create_app(db_path=self.db_path)
        self.client = self.app.test_client()

    def tearDown(self):
        os.remove(self.db_path)

    def test_health(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'status': 'ok'})

    def test_create_item(self):
        response = self.client.post('/api/inventory', json={'name': 'Widget', 'quantity': 5, 'price': 3.5})
        self.assertEqual(response.status_code, 201)
        body = response.get_json()
        self.assertEqual(body['name'], 'Widget')
        self.assertIn('id', body)

    def test_create_item_missing_name(self):
        response = self.client.post('/api/inventory', json={'quantity': 5})
        self.assertEqual(response.status_code, 400)

    def test_list_items_empty(self):
        response = self.client.get('/api/inventory')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_list_items_after_create(self):
        self.client.post('/api/inventory', json={'name': 'A'})
        self.client.post('/api/inventory', json={'name': 'B'})
        response = self.client.get('/api/inventory')
        self.assertEqual(len(response.get_json()), 2)

    def test_get_single_item(self):
        created = self.client.post('/api/inventory', json={'name': 'Widget'}).get_json()
        response = self.client.get(f"/api/inventory/{created['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['name'], 'Widget')

    def test_get_single_item_not_found(self):
        response = self.client.get('/api/inventory/9999')
        self.assertEqual(response.status_code, 404)

    def test_search_items(self):
        self.client.post('/api/inventory', json={'name': 'Chocolate Bar'})
        self.client.post('/api/inventory', json={'name': 'Milk'})
        response = self.client.get('/api/inventory/search?q=Bar')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_search_items_missing_query(self):
        response = self.client.get('/api/inventory/search')
        self.assertEqual(response.status_code, 400)

    def test_update_item(self):
        created = self.client.post('/api/inventory', json={'name': 'Widget', 'quantity': 1}).get_json()
        response = self.client.patch(f"/api/inventory/{created['id']}", json={'quantity': 99})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['quantity'], 99)

    def test_update_item_not_found(self):
        response = self.client.patch('/api/inventory/9999', json={'quantity': 1})
        self.assertEqual(response.status_code, 404)

    def test_delete_item(self):
        created = self.client.post('/api/inventory', json={'name': 'Widget'}).get_json()
        response = self.client.delete(f"/api/inventory/{created['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(f"/api/inventory/{created['id']}").status_code, 404)

    def test_delete_item_not_found(self):
        response = self.client.delete('/api/inventory/9999')
        self.assertEqual(response.status_code, 404)

    @patch('app.fetch_product_by_barcode')
    def test_external_barcode_lookup(self, mock_fetch):
        mock_fetch.return_value = {'name': 'Peanut Butter', 'barcode': '12345', 'brand': 'Acme', 'category': 'Spreads', 'image_url': 'http://example.com/img.jpg'}
        response = self.client.get('/api/external/barcode/12345')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['name'], 'Peanut Butter')

    @patch('app.fetch_product_by_barcode')
    def test_external_barcode_lookup_not_found(self, mock_fetch):
        mock_fetch.return_value = None
        response = self.client.get('/api/external/barcode/00000')
        self.assertEqual(response.status_code, 404)

    @patch('app.search_products_by_name')
    def test_external_search(self, mock_search):
        mock_search.return_value = [{'name': 'Cheddar Cheese', 'barcode': '999', 'brand': 'Dairy Co', 'category': 'Cheese', 'image_url': None}]
        response = self.client.get('/api/external/search?q=cheese')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    @patch('app.fetch_product_by_barcode')
    def test_import_from_barcode_adds_to_inventory(self, mock_fetch):
        mock_fetch.return_value = {'name': 'Peanut Butter', 'barcode': '12345', 'brand': 'Acme', 'category': 'Spreads', 'image_url': 'http://example.com/img.jpg'}
        response = self.client.post('/api/inventory/import/barcode', json={'barcode': '12345', 'quantity': 3, 'price': 4.99})
        self.assertEqual(response.status_code, 201)
        body = response.get_json()
        self.assertEqual(body['name'], 'Peanut Butter')
        self.assertEqual(body['quantity'], 3)
        listing = self.client.get('/api/inventory').get_json()
        self.assertEqual(len(listing), 1)
        self.assertEqual(listing[0]['barcode'], '12345')

    @patch('app.fetch_product_by_barcode')
    def test_import_from_barcode_not_found(self, mock_fetch):
        mock_fetch.return_value = None
        response = self.client.post('/api/inventory/import/barcode', json={'barcode': '00000'})
        self.assertEqual(response.status_code, 404)

    def test_import_from_barcode_missing_barcode(self):
        response = self.client.post('/api/inventory/import/barcode', json={})
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
