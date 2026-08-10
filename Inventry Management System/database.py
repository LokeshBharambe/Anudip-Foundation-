import sqlite3
from contextlib import contextmanager

DATABASE_NAME = "inventory.db"


@contextmanager
def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)

    # Return rows like dictionaries
    connection.row_factory = sqlite3.Row

    # Foreign-key support
    connection.execute("PRAGMA foreign_keys = ON")

    # Better read concurrency
    connection.execute("PRAGMA journal_mode = WAL")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                quantity INTEGER NOT NULL DEFAULT 0
                    CHECK(quantity >= 0),
                supplier TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes improve search/filter performance
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_name
            ON products(name)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_category
            ON products(category)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_quantity
            ON products(quantity)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_supplier
            ON products(supplier)
        """)