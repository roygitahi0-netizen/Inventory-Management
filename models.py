import os
import sqlite3


def init_db(db_path="inventory.db"):
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                barcode TEXT,
                category TEXT,
                brand TEXT,
                quantity INTEGER NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0.0
            )
            """
        )
        conn.commit()


class InventoryRepository:
    def __init__(self, db_path="inventory.db"):
        self.db_path = db_path
        init_db(self.db_path)

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_dict(self, row):
        return dict(row) if row is not None else None

    def create_item(self, name, barcode=None, category=None, brand=None, quantity=0, price=0.0):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name is required")

        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO inventory (name, barcode, category, brand, quantity, price)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name.strip(), barcode, category, brand, int(quantity), float(price)),
            )
            conn.commit()
            return self.get_item(cursor.lastrowid)

    def get_all_items(self, category=None, low_stock_threshold=None, min_price=None, max_price=None):
        query = "SELECT * FROM inventory WHERE 1=1"
        params = []

        if category is not None:
            query += " AND category = ?"
            params.append(category)
        if low_stock_threshold is not None:
            query += " AND quantity <= ?"
            params.append(int(low_stock_threshold))
        if min_price is not None:
            query += " AND price >= ?"
            params.append(float(min_price))
        if max_price is not None:
            query += " AND price <= ?"
            params.append(float(max_price))

        query += " ORDER BY id"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_item(self, item_id):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM inventory WHERE id = ?", (item_id,)).fetchone()
            return dict(row) if row is not None else None

    def search_by_name(self, query):
        term = f"%{query.strip()}%"
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM inventory WHERE lower(name) LIKE lower(?) ORDER BY id",
                (term,),
            ).fetchall()
            return [dict(row) for row in rows]

    def get_by_barcode(self, barcode):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM inventory WHERE barcode = ?", (barcode,)).fetchone()
            return dict(row) if row is not None else None

    def update_item(self, item_id, **updates):
        allowed = {"name", "barcode", "category", "brand", "quantity", "price"}
        filtered = {key: value for key, value in updates.items() if key in allowed and value is not None}

        if not filtered:
            return self.get_item(item_id)

        assignments = ", ".join(f"{key} = ?" for key in filtered)
        values = [filtered[key] for key in filtered]
        values.append(item_id)

        with self._connect() as conn:
            cursor = conn.execute(f"UPDATE inventory SET {assignments} WHERE id = ?", values)
            conn.commit()
            if cursor.rowcount == 0:
                return None
            return self.get_item(item_id)

    def delete_item(self, item_id):
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0
