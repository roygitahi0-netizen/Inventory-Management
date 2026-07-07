import unittest
from unittest.mock import MagicMock, patch

import requests

from external_api import (
    ExternalAPIError,
    fetch_product_by_barcode,
    search_products_by_name,
)


class TestFetchProductByBarcode(unittest.TestCase):
    @patch("external_api.requests.get")
    def test_fetch_product_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Peanut Butter",
                "code": "12345",
                "brands": "Acme",
                "categories": "Spreads,Snacks",
                "image_front_url": "http://example.com/img.jpg",
            },
        }
        mock_get.return_value = mock_response

        product = fetch_product_by_barcode("12345")

        self.assertEqual(product["name"], "Peanut Butter")
        self.assertEqual(product["barcode"], "12345")
        self.assertEqual(product["brand"], "Acme")
        self.assertEqual(product["category"], "Spreads")

    @patch("external_api.requests.get")
    def test_fetch_product_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status": 0}
        mock_get.return_value = mock_response

        product = fetch_product_by_barcode("00000")
        self.assertIsNone(product)

    @patch("external_api.requests.get")
    def test_fetch_product_network_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError("boom")
        with self.assertRaises(ExternalAPIError):
            fetch_product_by_barcode("12345")


class TestSearchProductsByName(unittest.TestCase):
    @patch("external_api.requests.get")
    def test_search_returns_normalized_products(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "products": [
                {"product_name": "Cheddar Cheese", "code": "111", "brands": "Dairy Co", "categories": "Cheese"},
                {"product_name": "Swiss Cheese", "code": "222", "brands": "Dairy Co", "categories": "Cheese"},
            ]
        }
        mock_get.return_value = mock_response

        results = search_products_by_name("cheese")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "Cheddar Cheese")

    @patch("external_api.requests.get")
    def test_search_no_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"products": []}
        mock_get.return_value = mock_response

        results = search_products_by_name("doesnotexist")
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()