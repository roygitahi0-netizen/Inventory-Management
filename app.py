import os
import warnings
from flask import Flask, jsonify, request

from models import InventoryRepository, init_db
from external_api import ExternalAPIError, fetch_product_by_barcode, search_products_by_name

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def create_app(db_path=None):
    app = Flask(__name__)
    db_path = db_path or os.environ.get("INVENTORY_DB_PATH", "inventory.db")
    init_db(db_path)
    repo = InventoryRepository(db_path)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/inventory")
    def list_items():
        category = request.args.get("category")
        low_stock_threshold = request.args.get("low_stock_threshold", type=int)
        min_price = request.args.get("min_price", type=float)
        max_price = request.args.get("max_price", type=float)
        items = repo.get_all_items(
            category=category,
            low_stock_threshold=low_stock_threshold,
            min_price=min_price,
            max_price=max_price,
        )
        return jsonify(items)

    @app.post("/api/inventory")
    def create_item():
        payload = request.get_json(silent=True) or {}
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "name is required"}), 400

        item = repo.create_item(
            name=name,
            barcode=payload.get("barcode"),
            category=payload.get("category"),
            brand=payload.get("brand"),
            quantity=payload.get("quantity", 0),
            price=payload.get("price", 0.0),
        )
        return jsonify(item), 201

    @app.get("/api/inventory/<int:item_id>")
    def get_item(item_id):
        item = repo.get_item(item_id)
        if item is None:
            return jsonify({"error": "item not found"}), 404
        return jsonify(item)

    @app.get("/api/inventory/search")
    def search_items():
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"error": "q is required"}), 400
        return jsonify(repo.search_by_name(query))

    @app.patch("/api/inventory/<int:item_id>")
    def update_item(item_id):
        payload = request.get_json(silent=True) or {}
        item = repo.update_item(item_id, **payload)
        if item is None:
            return jsonify({"error": "item not found"}), 404
        return jsonify(item)

    @app.delete("/api/inventory/<int:item_id>")
    def delete_item(item_id):
        deleted = repo.delete_item(item_id)
        if not deleted:
            return jsonify({"error": "item not found"}), 404
        return jsonify({"message": "deleted"})

    @app.get("/api/external/barcode/<barcode>")
    def external_barcode(barcode):
        try:
            product = fetch_product_by_barcode(barcode)
        except ExternalAPIError as exc:
            return jsonify({"error": str(exc)}), 502

        if product is None:
            return jsonify({"error": "product not found"}), 404
        return jsonify(product)

    @app.get("/api/external/search")
    def external_search():
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"error": "q is required"}), 400

        try:
            products = search_products_by_name(query)
        except ExternalAPIError as exc:
            return jsonify({"error": str(exc)}), 502
        return jsonify(products)

    @app.post("/api/inventory/import/barcode")
    def import_from_barcode():
        payload = request.get_json(silent=True) or {}
        barcode = payload.get("barcode")
        if not barcode:
            return jsonify({"error": "barcode is required"}), 400

        try:
            product = fetch_product_by_barcode(barcode)
        except ExternalAPIError as exc:
            return jsonify({"error": str(exc)}), 502

        if product is None:
            return jsonify({"error": "product not found"}), 404

        item = repo.create_item(
            name=product["name"],
            barcode=barcode,
            category=product.get("category"),
            brand=product.get("brand"),
            quantity=payload.get("quantity", 0),
            price=payload.get("price", 0.0),
        )
        return jsonify(item), 201

    return app


app = create_app()


if __name__ == "__main__":
    import logging

    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    logging.getLogger("flask.app").setLevel(logging.ERROR)
    
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
