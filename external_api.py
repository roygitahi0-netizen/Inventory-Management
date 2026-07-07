import requests


class ExternalAPIError(RuntimeError):
    pass


API_BASE_URL = "https://world.openfoodfacts.org"


def _normalize_product(raw_product):
    return {
        "name": raw_product.get("product_name") or raw_product.get("name"),
        "barcode": raw_product.get("code") or raw_product.get("barcode"),
        "brand": raw_product.get("brands") or raw_product.get("brand"),
        "category": (raw_product.get("categories") or "").split(",")[0].strip(),
        "image_url": raw_product.get("image_front_url") or raw_product.get("image_url"),
    }


def fetch_product_by_barcode(barcode):
    try:
        response = requests.get(f"{API_BASE_URL}/api/v2/product/{barcode}.json", timeout=10)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise ExternalAPIError(str(exc)) from exc

    if payload.get("status") != 1:
        return None

    product = payload.get("product") or {}
    return _normalize_product(product)


def search_products_by_name(query):
    try:
        response = requests.get(
            f"{API_BASE_URL}/cgi/search.pl",
            params={"search_terms": query, "search_simple": 1, "action": "process", "json": 1},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise ExternalAPIError(str(exc)) from exc

    products = payload.get("products", [])
    return [_normalize_product(product) for product in products]
