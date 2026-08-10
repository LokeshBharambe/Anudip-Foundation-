import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_NAME = "inventory.db"
LOW_STOCK_LIMIT = 10


# ============================================================
# DATABASE
# ============================================================

class Database:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.initialize()

    def connect(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def initialize(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL CHECK(price >= 0),
                    quantity INTEGER NOT NULL CHECK(quantity >= 0),
                    supplier TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_name
                ON products(name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_category
                ON products(category)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_supplier
                ON products(supplier)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_quantity
                ON products(quantity)
            """)

    def add_product(self, name, category, price, quantity, supplier):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            cur = conn.execute("""
                INSERT INTO products
                (name, category, price, quantity, supplier, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, category, price, quantity, supplier, now, now))
            return cur.lastrowid

    def update_product(self, product_id, name, category, price, quantity, supplier):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.connect() as conn:
            cur = conn.execute("""
                UPDATE products
                SET name=?, category=?, price=?, quantity=?,
                    supplier=?, updated_at=?
                WHERE id=?
            """, (name, category, price, quantity, supplier, now, product_id))
            return cur.rowcount > 0

    def delete_product(self, product_id):
        with self.connect() as conn:
            cur = conn.execute(
                "DELETE FROM products WHERE id=?", (product_id,)
            )
            return cur.rowcount > 0

    def get_product(self, product_id):
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM products WHERE id=?", (product_id,)
            ).fetchone()

    def get_categories(self):
        with self.connect() as conn:
            rows = conn.execute("""
                SELECT DISTINCT category
                FROM products
                WHERE category <> ''
                ORDER BY category
            """).fetchall()
            return [row["category"] for row in rows]

    def search_products(self, search="", category="All", stock="All"):
        query = """
            SELECT * FROM products
            WHERE (name LIKE ? OR category LIKE ? OR supplier LIKE ?)
        """
        params = [f"%{search}%", f"%{search}%", f"%{search}%"]

        if category != "All":
            query += " AND category = ?"
            params.append(category)

        if stock == "Low Stock":
            query += " AND quantity <= ?"
            params.append(LOW_STOCK_LIMIT)
        elif stock == "Out of Stock":
            query += " AND quantity = 0"
        elif stock == "In Stock":
            query += " AND quantity > ?"
            params.append(LOW_STOCK_LIMIT)

        query += " ORDER BY id DESC"

        with self.connect() as conn:
            return conn.execute(query, params).fetchall()

    def dashboard_stats(self):
        with self.connect() as conn:
            stats = conn.execute("""
                SELECT
                    COUNT(*) AS products,
                    COALESCE(SUM(quantity), 0) AS units,
                    COALESCE(SUM(price * quantity), 0) AS value,
                    COALESCE(SUM(
                        CASE WHEN quantity <= ? THEN 1 ELSE 0 END
                    ), 0) AS low_stock,
                    COALESCE(SUM(
                        CASE WHEN quantity = 0 THEN 1 ELSE 0 END
                    ), 0) AS out_stock
                FROM products
            """, (LOW_STOCK_LIMIT,)).fetchone()
            return stats

    def category_summary(self):
        with self.connect() as conn:
            return conn.execute("""
                SELECT category,
                       COUNT(*) AS products,
                       COALESCE(SUM(quantity), 0) AS units,
                       COALESCE(SUM(price * quantity), 0) AS value
                FROM products
                GROUP BY category
                ORDER BY value DESC
            """).fetchall()


# ============================================================
# APPLICATION
# ============================================================

class InventoryApp:
    BG = "#f4f6f8"
    SIDEBAR = "#263238"
    SIDEBAR_HOVER = "#37474f"
    TEXT = "#263238"
    MUTED = "#6b7280"
    BORDER = "#d9dee3"
    WHITE = "#ffffff"
    ACCENT = "#1976d2"
    ACCENT_DARK = "#1565c0"
    SUCCESS = "#2e7d32"
    WARNING = "#ef8b00"
    DANGER = "#c62828"

    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.selected_id = None
        self.current_page = "Dashboard"

        self.root.title("Inventory Management System")
        self.root.geometry("1200x720")
        self.root.minsize(1000, 620)
        self.root.configure(bg=self.BG)

        self.setup_style()
        self.build_layout()
        self.show_dashboard()
        self.refresh_all()

    # --------------------------------------------------------
    # STYLE
    # --------------------------------------------------------

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=self.WHITE,
            foreground=self.TEXT,
            fieldbackground=self.WHITE,
            rowheight=32,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background="#eef1f4",
            foreground=self.TEXT,
            font=("Segoe UI", 10, "bold"),
            padding=8
        )
        style.map(
            "Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", self.TEXT)]
        )
        style.configure(
            "TCombobox",
            padding=6
        )
        style.configure(
            "TEntry",
            padding=7
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=(12, 7)
        )
        style.configure(
            "Accent.TButton",
            background=self.ACCENT,
            foreground="white",
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "Accent.TButton",
            background=[("active", self.ACCENT_DARK)]
        )
        style.configure(
            "Danger.TButton",
            background="#fbe9e7",
            foreground=self.DANGER,
            font=("Segoe UI", 10, "bold")
        )

    # --------------------------------------------------------
    # MAIN LAYOUT
    # --------------------------------------------------------

    def build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=self.SIDEBAR, width=215)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main = tk.Frame(self.root, bg=self.BG)
        self.main.pack(side="right", fill="both", expand=True)

        # Sidebar header
        tk.Label(
            self.sidebar,
            text="INVENTORY",
            bg=self.SIDEBAR,
            fg="white",
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=22, pady=(28, 2))

        tk.Label(
            self.sidebar,
            text="Management System",
            bg=self.SIDEBAR,
            fg="#b0bec5",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=22, pady=(0, 28))

        self.nav_buttons = {}
        for name, command in [
            ("Dashboard", self.show_dashboard),
            ("Products", self.show_products),
            ("Stock Alerts", self.show_stock_alerts),
            ("Reports", self.show_reports),
        ]:
            self.add_nav_button(name, command)

        tk.Frame(self.sidebar, bg="#455a64", height=1).pack(
            fill="x", padx=18, pady=18
        )

        tk.Label(
            self.sidebar,
            text="Database",
            bg=self.SIDEBAR,
            fg="#90a4ae",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=22, pady=(0, 6))

        tk.Label(
            self.sidebar,
            text="SQLite • Local",
            bg=self.SIDEBAR,
            fg="#cfd8dc",
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=22)

        # Main top bar
        self.topbar = tk.Frame(self.main, bg=self.WHITE, height=62)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        self.page_title = tk.Label(
            self.topbar,
            text="Dashboard",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 17, "bold")
        )
        self.page_title.pack(side="left", padx=25)

        self.status_text = tk.StringVar(value="Ready")
        tk.Label(
            self.topbar,
            textvariable=self.status_text,
            bg=self.WHITE,
            fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(side="right", padx=25)

        self.content = tk.Frame(self.main, bg=self.BG)
        self.content.pack(fill="both", expand=True)

        # Bottom status bar
        self.statusbar = tk.Frame(self.main, bg="#e9edf0", height=27)
        self.statusbar.pack(fill="x", side="bottom")
        self.statusbar.pack_propagate(False)

        self.footer_text = tk.StringVar(value="Ready")
        tk.Label(
            self.statusbar,
            textvariable=self.footer_text,
            bg="#e9edf0",
            fg=self.MUTED,
            font=("Segoe UI", 8)
        ).pack(side="left", padx=15)

    def add_nav_button(self, text, command):
        btn = tk.Button(
            self.sidebar,
            text="  " + text,
            command=command,
            anchor="w",
            relief="flat",
            bd=0,
            bg=self.SIDEBAR,
            fg="#eceff1",
            activebackground=self.SIDEBAR_HOVER,
            activeforeground="white",
            font=("Segoe UI", 10),
            padx=14,
            pady=11,
            cursor="hand2"
        )
        btn.pack(fill="x", padx=12, pady=2)
        self.nav_buttons[text] = btn

    def set_active_nav(self, name):
        for key, btn in self.nav_buttons.items():
            btn.configure(bg=self.SIDEBAR_HOVER if key == name else self.SIDEBAR)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def set_page(self, title, nav_name):
        self.current_page = title
        self.page_title.configure(text=title)
        self.set_active_nav(nav_name)
        self.clear_content()

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    def show_dashboard(self):
        self.set_page("Dashboard", "Dashboard")

        frame = tk.Frame(self.content, bg=self.BG)
        frame.pack(fill="both", expand=True, padx=25, pady=22)

        stats = self.db.dashboard_stats()

        cards = [
            ("PRODUCTS", str(stats["products"]), self.ACCENT),
            ("STOCK UNITS", f"{stats['units']:,}", self.SUCCESS),
            ("LOW STOCK", str(stats["low_stock"]), self.WARNING),
            ("INVENTORY VALUE", f"₹{stats['value']:,.2f}", self.DANGER),
        ]

        cards_frame = tk.Frame(frame, bg=self.BG)
        cards_frame.pack(fill="x")

        for title, value, accent in cards:
            card = tk.Frame(
                cards_frame,
                bg=self.WHITE,
                highlightbackground=self.BORDER,
                highlightthickness=1
            )
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))

            tk.Frame(card, bg=accent, width=5).pack(side="left", fill="y")

            inside = tk.Frame(card, bg=self.WHITE)
            inside.pack(fill="both", expand=True, padx=15, pady=13)

            tk.Label(
                inside,
                text=title,
                bg=self.WHITE,
                fg=self.MUTED,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")

            tk.Label(
                inside,
                text=value,
                bg=self.WHITE,
                fg=self.TEXT,
                font=("Segoe UI", 19, "bold")
            ).pack(anchor="w", pady=(5, 0))

        # Recent products
        section = tk.Frame(
            frame,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )
        section.pack(fill="both", expand=True, pady=(20, 0))

        head = tk.Frame(section, bg=self.WHITE)
        head.pack(fill="x", padx=18, pady=15)

        tk.Label(
            head,
            text="Recent Products",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        tk.Button(
            head,
            text="View all",
            command=self.show_products,
            relief="flat",
            bd=0,
            bg=self.WHITE,
            fg=self.ACCENT,
            cursor="hand2",
            font=("Segoe UI", 9, "bold")
        ).pack(side="right")

        self.create_table(
            section,
            compact=True,
            rows=self.db.search_products()
        )

    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

    def show_products(self):
        self.set_page("Products", "Products")

        outer = tk.Frame(self.content, bg=self.BG)
        outer.pack(fill="both", expand=True, padx=25, pady=20)

        # Search/filter area
        filters = tk.Frame(
            outer,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )
        filters.pack(fill="x", pady=(0, 12))

        tk.Label(
            filters,
            text="Search",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=0, padx=(15, 5), pady=13, sticky="w")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_product_table())

        ttk.Entry(
            filters,
            textvariable=self.search_var,
            width=28
        ).grid(row=0, column=1, padx=5, pady=13)

        tk.Label(
            filters,
            text="Category",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=2, padx=(18, 5), pady=13)

        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(
            filters,
            textvariable=self.category_var,
            state="readonly",
            width=18,
            values=["All"] + self.db.get_categories()
        )
        self.category_combo.grid(row=0, column=3, padx=5, pady=13)
        self.category_combo.bind("<<ComboboxSelected>>",
                                 lambda e: self.refresh_product_table())

        tk.Label(
            filters,
            text="Stock",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=4, padx=(18, 5), pady=13)

        self.stock_var = tk.StringVar(value="All")
        self.stock_combo = ttk.Combobox(
            filters,
            textvariable=self.stock_var,
            state="readonly",
            width=15,
            values=["All", "In Stock", "Low Stock", "Out of Stock"]
        )
        self.stock_combo.grid(row=0, column=5, padx=5, pady=13)
        self.stock_combo.bind("<<ComboboxSelected>>",
                              lambda e: self.refresh_product_table())

        ttk.Button(
            filters,
            text="Clear",
            command=self.clear_filters
        ).grid(row=0, column=6, padx=15)

        ttk.Button(
            filters,
            text="+ Add Product",
            style="Accent.TButton",
            command=self.open_product_form
        ).grid(row=0, column=7, padx=(0, 15))

        # Table
        table_box = tk.Frame(
            outer,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )
        table_box.pack(fill="both", expand=True)

        self.product_table = self.create_table(
            table_box,
            compact=False,
            rows=[]
        )
        self.product_table.bind("<Double-1>", self.edit_selected_product)

        # Actions
        actions = tk.Frame(outer, bg=self.BG)
        actions.pack(fill="x", pady=(10, 0))

        ttk.Button(
            actions,
            text="Edit Selected",
            command=self.edit_selected_product
        ).pack(side="left")

        ttk.Button(
            actions,
            text="Delete Selected",
            style="Danger.TButton",
            command=self.delete_selected_product
        ).pack(side="left", padx=8)

        ttk.Button(
            actions,
            text="Refresh",
            command=self.refresh_product_table
        ).pack(side="right")

        self.refresh_product_table()

    def refresh_product_table(self):
        if not hasattr(self, "product_table") or not self.product_table.winfo_exists():
            return

        products = self.db.search_products(
            self.search_var.get(),
            self.category_var.get(),
            self.stock_var.get()
        )
        self.fill_table(self.product_table, products)
        self.footer_text.set(f"{len(products)} product(s) shown")
        self.status_text.set("Product list updated")

    def clear_filters(self):
        self.search_var.set("")
        self.category_var.set("All")
        self.stock_var.set("All")
        self.refresh_product_table()

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    def create_table(self, parent, compact=False, rows=None):
        columns = ("id", "name", "category", "price", "quantity", "supplier")

        box = tk.Frame(parent, bg=self.WHITE)
        box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        tree = ttk.Treeview(
            box,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "id": "ID",
            "name": "Product",
            "category": "Category",
            "price": "Price",
            "quantity": "Qty",
            "supplier": "Supplier"
        }

        widths = {
            "id": 55,
            "name": 240,
            "category": 150,
            "price": 110,
            "quantity": 75,
            "supplier": 180
        }

        for col in columns:
            tree.heading(
                col,
                text=headings[col],
                command=lambda c=col: self.sort_tree(tree, c, False)
            )
            tree.column(
                col,
                width=widths[col],
                anchor="center" if col in ("id", "price", "quantity") else "w"
            )

        tree.tag_configure("low", background="#fff7e6")
        tree.tag_configure("out", background="#fdecec")

        scrollbar = ttk.Scrollbar(
            box,
            orient="vertical",
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if rows:
            self.fill_table(tree, rows)

        return tree

    def fill_table(self, tree, rows):
        for item in tree.get_children():
            tree.delete(item)

        for row in rows:
            tag = ()
            if row["quantity"] == 0:
                tag = ("out",)
            elif row["quantity"] <= LOW_STOCK_LIMIT:
                tag = ("low",)

            tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["name"],
                    row["category"],
                    f"₹{row['price']:,.2f}",
                    row["quantity"],
                    row["supplier"]
                ),
                tags=tag
            )

    def sort_tree(self, tree, col, reverse):
        data = [(tree.set(item, col), item)
                for item in tree.get_children("")]

        def key(value):
            text = value[0].replace("₹", "").replace(",", "")
            try:
                return float(text)
            except ValueError:
                return text.lower()

        data.sort(key=key, reverse=reverse)

        for index, (_, item) in enumerate(data):
            tree.move(item, "", index)

        tree.heading(
            col,
            command=lambda: self.sort_tree(tree, col, not reverse)
        )

    # --------------------------------------------------------
    # PRODUCT FORM
    # --------------------------------------------------------

    def open_product_form(self, product=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Product" if product else "Add Product")
        dialog.geometry("500x455")
        dialog.resizable(False, False)
        dialog.configure(bg=self.BG)
        dialog.transient(self.root)
        dialog.grab_set()

        title = "Edit Product" if product else "Add New Product"

        tk.Label(
            dialog,
            text=title,
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=28, pady=(25, 18))

        form = tk.Frame(
            dialog,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )
        form.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        fields = [
            ("Product Name", "name"),
            ("Category", "category"),
            ("Price", "price"),
            ("Quantity", "quantity"),
            ("Supplier", "supplier")
        ]

        entries = {}

        for row, (label, key) in enumerate(fields):
            tk.Label(
                form,
                text=label,
                bg=self.WHITE,
                fg=self.TEXT,
                font=("Segoe UI", 9, "bold")
            ).grid(row=row, column=0, padx=20, pady=9, sticky="w")

            entry = ttk.Entry(form, width=34)
            entry.grid(row=row, column=1, padx=20, pady=9)
            entries[key] = entry

        if product:
            entries["name"].insert(0, product["name"])
            entries["category"].insert(0, product["category"])
            entries["price"].insert(0, str(product["price"]))
            entries["quantity"].insert(0, str(product["quantity"]))
            entries["supplier"].insert(0, product["supplier"])

        buttons = tk.Frame(form, bg=self.WHITE)
        buttons.grid(row=5, column=0, columnspan=2, pady=20)

        def save():
            name = entries["name"].get().strip()
            category = entries["category"].get().strip()
            supplier = entries["supplier"].get().strip()

            if not name or not category:
                messagebox.showwarning(
                    "Validation",
                    "Product name and category are required.",
                    parent=dialog
                )
                return

            try:
                price = float(entries["price"].get())
                quantity = int(entries["quantity"].get())

                if price < 0 or quantity < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "Validation",
                    "Enter a valid non-negative price and quantity.",
                    parent=dialog
                )
                return

            try:
                if product:
                    self.db.update_product(
                        product["id"],
                        name, category, price, quantity, supplier
                    )
                    self.status_text.set("Product updated")
                    self.footer_text.set(
                        f"Product #{product['id']} updated"
                    )
                else:
                    new_id = self.db.add_product(
                        name, category, price, quantity, supplier
                    )
                    self.status_text.set("Product added")
                    self.footer_text.set(
                        f"Product #{new_id} added"
                    )

                dialog.destroy()
                self.refresh_all()
                if self.current_page == "Products":
                    self.refresh_product_table()

            except Exception as exc:
                messagebox.showerror(
                    "Database Error",
                    str(exc),
                    parent=dialog
                )

        ttk.Button(
            buttons,
            text="Save",
            style="Accent.TButton",
            command=save
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="left", padx=5)

        entries["name"].focus_set()

    def edit_selected_product(self, event=None):
        if not hasattr(self, "product_table"):
            return

        selection = self.product_table.selection()

        if not selection:
            messagebox.showinfo(
                "Select Product",
                "Select a product first."
            )
            return

        values = self.product_table.item(selection[0], "values")
        product_id = int(values[0])
        product = self.db.get_product(product_id)

        if product:
            self.open_product_form(product)

    def delete_selected_product(self):
        if not hasattr(self, "product_table"):
            return

        selection = self.product_table.selection()

        if not selection:
            messagebox.showinfo(
                "Select Product",
                "Select a product first."
            )
            return

        values = self.product_table.item(selection[0], "values")
        product_id = int(values[0])
        product_name = values[1]

        confirm = messagebox.askyesno(
            "Delete Product",
            f"Delete '{product_name}' from inventory?"
        )

        if not confirm:
            return

        if self.db.delete_product(product_id):
            self.footer_text.set(
                f"Product #{product_id} deleted"
            )
            self.status_text.set("Product deleted")
            self.refresh_all()
            self.refresh_product_table()

    # --------------------------------------------------------
    # STOCK ALERTS
    # --------------------------------------------------------

    def show_stock_alerts(self):
        self.set_page("Stock Alerts", "Stock Alerts")

        outer = tk.Frame(self.content, bg=self.BG)
        outer.pack(fill="both", expand=True, padx=25, pady=20)

        stats = self.db.dashboard_stats()

        header = tk.Frame(outer, bg=self.BG)
        header.pack(fill="x", pady=(0, 15))

        tk.Label(
            header,
            text=f"{stats['low_stock']} item(s) need attention",
            bg=self.BG,
            fg=self.WARNING if stats["low_stock"] else self.SUCCESS,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")

        tk.Label(
            header,
            text=f"Low stock limit: {LOW_STOCK_LIMIT} units",
            bg=self.BG,
            fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(side="right")

        box = tk.Frame(
            outer,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )
        box.pack(fill="both", expand=True)

        products = self.db.search_products(stock="Low Stock")
        table = self.create_table(box, rows=products)
        table.bind(
            "<Double-1>",
            lambda e: self.edit_stock_from_table(table)
        )

    def edit_stock_from_table(self, table):
        selection = table.selection()
        if not selection:
            return

        values = table.item(selection[0], "values")
        product = self.db.get_product(int(values[0]))
        if product:
            self.open_product_form(product)

    # --------------------------------------------------------
    # REPORTS
    # --------------------------------------------------------

    def show_reports(self):
        self.set_page("Reports", "Reports")

        outer = tk.Frame(self.content, bg=self.BG)
        outer.pack(fill="both", expand=True, padx=25, pady=20)

        stats = self.db.dashboard_stats()

        summary = tk.Frame(
            outer,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )
        summary.pack(fill="x")

        tk.Label(
            summary,
            text="Inventory Summary",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=18, pady=(16, 5))

        lines = [
            ("Total products", stats["products"]),
            ("Total stock units", f"{stats['units']:,}"),
            ("Low-stock products", stats["low_stock"]),
            ("Out-of-stock products", stats["out_stock"]),
            ("Total inventory value", f"₹{stats['value']:,.2f}")
        ]

        for label, value in lines:
            row = tk.Frame(summary, bg=self.WHITE)
            row.pack(fill="x", padx=18, pady=5)

            tk.Label(
                row,
                text=label,
                bg=self.WHITE,
                fg=self.MUTED,
                font=("Segoe UI", 10)
            ).pack(side="left")

            tk.Label(
                row,
                text=str(value),
                bg=self.WHITE,
                fg=self.TEXT,
                font=("Segoe UI", 10, "bold")
            ).pack(side="right")

        cat_box = tk.Frame(
            outer,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )
        cat_box.pack(fill="both", expand=True, pady=(15, 0))

        tk.Label(
            cat_box,
            text="Category Summary",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=18, pady=15)

        columns = ("category", "products", "units", "value")
        tree = ttk.Treeview(
            cat_box,
            columns=columns,
            show="headings"
        )

        for col, heading in zip(
            columns,
            ["Category", "Products", "Units", "Inventory Value"]
        ):
            tree.heading(col, text=heading)
            tree.column(
                col,
                width=180,
                anchor="center" if col != "category" else "w"
            )

        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for row in self.db.category_summary():
            tree.insert(
                "",
                "end",
                values=(
                    row["category"],
                    row["products"],
                    row["units"],
                    f"₹{row['value']:,.2f}"
                )
            )

    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    def refresh_all(self):
        self.update_status()

        if self.current_page == "Dashboard":
            self.show_dashboard()
        elif self.current_page == "Stock Alerts":
            self.show_stock_alerts()
        elif self.current_page == "Reports":
            self.show_reports()

    def update_status(self):
        stats = self.db.dashboard_stats()
        self.status_text.set("Ready")
        self.footer_text.set(
            f"{stats['products']} products • "
            f"{stats['units']:,} stock units • "
            f"Low stock: {stats['low_stock']}"
        )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()