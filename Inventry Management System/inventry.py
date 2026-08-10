from database import get_connection


class InventoryManager:

    # -------------------------
    # CREATE
    # -------------------------
    def add_product(
        self,
        name,
        category,
        price,
        quantity,
        supplier=None
    ):
        if not name.strip():
            raise ValueError("Product name cannot be empty.")

        if price < 0:
            raise ValueError("Price cannot be negative.")

        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO products
                (name, category, price, quantity, supplier)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name.strip(),
                category.strip(),
                price,
                quantity,
                supplier
            ))

            return cursor.lastrowid

    # -------------------------
    # READ - Single Product
    # -------------------------
    def get_product(self, product_id):

        with get_connection() as conn:
            product = conn.execute("""
                SELECT *
                FROM products
                WHERE id = ?
            """, (product_id,)).fetchone()

            return dict(product) if product else None

    # -------------------------
    # READ - All Products
    # -------------------------
    def get_products(self, page=1, page_size=20):

        if page < 1:
            raise ValueError("Page must be >= 1.")

        if page_size < 1:
            raise ValueError("Page size must be >= 1.")

        offset = (page - 1) * page_size

        with get_connection() as conn:

            products = conn.execute("""
                SELECT *
                FROM products
                ORDER BY id
                LIMIT ? OFFSET ?
            """, (page_size, offset)).fetchall()

            return [dict(product) for product in products]

    # -------------------------
    # SEARCH
    # -------------------------
    def search_products(self, keyword):

        keyword = keyword.strip()

        with get_connection() as conn:

            products = conn.execute("""
                SELECT *
                FROM products
                WHERE name LIKE ?
                   OR category LIKE ?
                   OR supplier LIKE ?
                ORDER BY name
            """, (
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%"
            )).fetchall()

            return [dict(product) for product in products]

    # -------------------------
    # UPDATE
    # -------------------------
    def update_product(
        self,
        product_id,
        name,
        category,
        price,
        quantity,
        supplier=None
    ):

        if price < 0:
            raise ValueError("Price cannot be negative.")

        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        with get_connection() as conn:

            cursor = conn.execute("""
                UPDATE products
                SET
                    name = ?,
                    category = ?,
                    price = ?,
                    quantity = ?,
                    supplier = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                name.strip(),
                category.strip(),
                price,
                quantity,
                supplier,
                product_id
            ))

            return cursor.rowcount > 0

    # -------------------------
    # DELETE
    # -------------------------
    def delete_product(self, product_id):

        with get_connection() as conn:

            cursor = conn.execute("""
                DELETE FROM products
                WHERE id = ?
            """, (product_id,))

            return cursor.rowcount > 0

    # -------------------------
    # STOCK UPDATE
    # -------------------------
    def update_stock(self, product_id, quantity_change):

        with get_connection() as conn:

            cursor = conn.execute("""
                UPDATE products
                SET
                    quantity = quantity + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                  AND quantity + ? >= 0
            """, (
                quantity_change,
                product_id,
                quantity_change
            ))

            return cursor.rowcount > 0

    # -------------------------
    # LOW STOCK PRODUCTS
    # -------------------------
    def low_stock_products(self, threshold=10):

        with get_connection() as conn:

            products = conn.execute("""
                SELECT *
                FROM products
                WHERE quantity <= ?
                ORDER BY quantity ASC
            """, (threshold,)).fetchall()

            return [dict(product) for product in products]

    # -------------------------
    # INVENTORY VALUE
    # -------------------------
    def inventory_value(self):

        with get_connection() as conn:

            result = conn.execute("""
                SELECT
                    COALESCE(SUM(price * quantity), 0)
                    AS total_value
                FROM products
            """).fetchone()

            return result["total_value"]