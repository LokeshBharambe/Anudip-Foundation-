import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


# ============================================================
# DATABASE
# ============================================================

class Database:

    def __init__(self, db_name="todo.db"):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row

        # Performance settings
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA synchronous=NORMAL")

        self.create_table()

    def create_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """

        self.connection.execute(query)

        # Indexes for faster searching/filtering
        self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_status
            ON tasks(status)
        """)

        self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON tasks(created_at)
        """)

        self.connection.commit()

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    def add_task(self, title, description):

        now = datetime.now().isoformat(timespec="seconds")

        query = """
        INSERT INTO tasks
        (title, description, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """

        self.connection.execute(
            query,
            (title, description, "Pending", now, now)
        )

        self.connection.commit()

    # --------------------------------------------------------
    # READ
    # --------------------------------------------------------

    def get_tasks(self, search=""):

        if search:

            query = """
            SELECT *
            FROM tasks
            WHERE title LIKE ?
               OR description LIKE ?
            ORDER BY id DESC
            """

            search_value = f"%{search}%"

            return self.connection.execute(
                query,
                (search_value, search_value)
            ).fetchall()

        else:

            query = """
            SELECT *
            FROM tasks
            ORDER BY id DESC
            """

            return self.connection.execute(query).fetchall()

    # --------------------------------------------------------
    # GET SINGLE TASK
    # --------------------------------------------------------

    def get_task(self, task_id):

        query = """
        SELECT *
        FROM tasks
        WHERE id = ?
        """

        return self.connection.execute(
            query,
            (task_id,)
        ).fetchone()

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update_task(self, task_id, title, description):

        now = datetime.now().isoformat(timespec="seconds")

        query = """
        UPDATE tasks
        SET title = ?,
            description = ?,
            updated_at = ?
        WHERE id = ?
        """

        self.connection.execute(
            query,
            (title, description, now, task_id)
        )

        self.connection.commit()

    # --------------------------------------------------------
    # MARK COMPLETED
    # --------------------------------------------------------

    def mark_completed(self, task_id):

        now = datetime.now().isoformat(timespec="seconds")

        query = """
        UPDATE tasks
        SET status = 'Completed',
            updated_at = ?
        WHERE id = ?
        """

        self.connection.execute(
            query,
            (now, task_id)
        )

        self.connection.commit()

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def delete_task(self, task_id):

        query = """
        DELETE FROM tasks
        WHERE id = ?
        """

        self.connection.execute(
            query,
            (task_id,)
        )

        self.connection.commit()

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------

    def close(self):
        self.connection.close()


# ============================================================
# GUI APPLICATION
# ============================================================

class TodoGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("To-Do Manager")
        self.root.geometry("1000x650")
        self.root.minsize(850, 550)

        self.db = Database()

        self.selected_task_id = None

        self.setup_style()
        self.create_widgets()

        self.load_tasks()

        # Close database properly
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

    # ========================================================
    # STYLE
    # ========================================================

    def setup_style(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "Title.TLabel",
            font=("Arial", 24, "bold")
        )

        style.configure(
            "Heading.TLabel",
            font=("Arial", 12, "bold")
        )

        style.configure(
            "Treeview",
            rowheight=32,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold")
        )

    # ========================================================
    # CREATE GUI
    # ========================================================

    def create_widgets(self):

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = ttk.Frame(self.root, padding=15)
        header.pack(fill="x")

        title = ttk.Label(
            header,
            text="📝 To-Do Manager",
            style="Title.TLabel"
        )

        title.pack(side="left")

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search_frame = ttk.Frame(
            self.root,
            padding=(15, 5)
        )

        search_frame.pack(fill="x")

        ttk.Label(
            search_frame,
            text="Search:"
        ).pack(side="left")

        self.search_entry = ttk.Entry(
            search_frame,
            width=40
        )

        self.search_entry.pack(
            side="left",
            padx=10
        )

        ttk.Button(
            search_frame,
            text="🔍 Search",
            command=self.search_tasks
        ).pack(side="left")

        ttk.Button(
            search_frame,
            text="Refresh",
            command=self.load_tasks
        ).pack(side="left", padx=5)

        # ----------------------------------------------------
        # INPUT FORM
        # ----------------------------------------------------

        form = ttk.LabelFrame(
            self.root,
            text=" Task Details ",
            padding=15
        )

        form.pack(
            fill="x",
            padx=15,
            pady=10
        )

        ttk.Label(
            form,
            text="Title:",
            style="Heading.TLabel"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=5,
            pady=5
        )

        self.title_entry = ttk.Entry(
            form,
            width=60
        )

        self.title_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=5,
            pady=5
        )

        ttk.Label(
            form,
            text="Description:",
            style="Heading.TLabel"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=5,
            pady=5
        )

        self.description_entry = ttk.Entry(
            form,
            width=60
        )

        self.description_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=5,
            pady=5
        )

        form.columnconfigure(1, weight=1)

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        button_frame = ttk.Frame(
            self.root,
            padding=(15, 5)
        )

        button_frame.pack(fill="x")

        ttk.Button(
            button_frame,
            text="➕ Add Task",
            command=self.add_task
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            button_frame,
            text="✏️ Update",
            command=self.update_task
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            button_frame,
            text="✅ Complete",
            command=self.complete_task
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            button_frame,
            text="🗑️ Delete",
            command=self.delete_task
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_form
        ).pack(
            side="left",
            padx=5
        )

        # ----------------------------------------------------
        # TASK TABLE
        # ----------------------------------------------------

        table_frame = ttk.Frame(
            self.root,
            padding=15
        )

        table_frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "id",
            "title",
            "description",
            "status",
            "created"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading(
            "id",
            text="ID"
        )

        self.tree.heading(
            "title",
            text="Title"
        )

        self.tree.heading(
            "description",
            text="Description"
        )

        self.tree.heading(
            "status",
            text="Status"
        )

        self.tree.heading(
            "created",
            text="Created"
        )

        self.tree.column(
            "id",
            width=50,
            anchor="center"
        )

        self.tree.column(
            "title",
            width=200
        )

        self.tree.column(
            "description",
            width=350
        )

        self.tree.column(
            "status",
            width=100,
            anchor="center"
        )

        self.tree.column(
            "created",
            width=160
        )

        # ----------------------------------------------------
        # SCROLLBAR
        # ----------------------------------------------------

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Select row
        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_task
        )

    # ========================================================
    # LOAD TASKS
    # ========================================================

    def load_tasks(self):

        self.search_entry.delete(
            0,
            tk.END
        )

        self.display_tasks()

    # ========================================================
    # DISPLAY TASKS
    # ========================================================

    def display_tasks(self, search=""):

        # Remove old rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        tasks = self.db.get_tasks(search)

        for task in tasks:

            self.tree.insert(
                "",
                "end",
                values=(
                    task["id"],
                    task["title"],
                    task["description"],
                    task["status"],
                    task["created_at"]
                )
            )

    # ========================================================
    # SEARCH
    # ========================================================

    def search_tasks(self):

        search = self.search_entry.get().strip()

        self.display_tasks(search)

    # ========================================================
    # SELECT TASK
    # ========================================================

    def select_task(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(
            selected[0],
            "values"
        )

        self.selected_task_id = int(values[0])

        self.title_entry.delete(
            0,
            tk.END
        )

        self.title_entry.insert(
            0,
            values[1]
        )

        self.description_entry.delete(
            0,
            tk.END
        )

        self.description_entry.insert(
            0,
            values[2]
        )

    # ========================================================
    # ADD TASK
    # ========================================================

    def add_task(self):

        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()

        if not title:

            messagebox.showwarning(
                "Validation Error",
                "Please enter a task title."
            )

            return

        self.db.add_task(
            title,
            description
        )

        messagebox.showinfo(
            "Success",
            "Task added successfully!"
        )

        self.clear_form()
        self.display_tasks()

    # ========================================================
    # UPDATE TASK
    # ========================================================

    def update_task(self):

        if self.selected_task_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a task first."
            )

            return

        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()

        if not title:

            messagebox.showwarning(
                "Validation Error",
                "Title cannot be empty."
            )

            return

        self.db.update_task(
            self.selected_task_id,
            title,
            description
        )

        messagebox.showinfo(
            "Success",
            "Task updated successfully!"
        )

        self.clear_form()
        self.display_tasks()

    # ========================================================
    # COMPLETE TASK
    # ========================================================

    def complete_task(self):

        if self.selected_task_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a task first."
            )

            return

        self.db.mark_completed(
            self.selected_task_id
        )

        messagebox.showinfo(
            "Success",
            "Task marked as completed!"
        )

        self.clear_form()
        self.display_tasks()

    # ========================================================
    # DELETE TASK
    # ========================================================

    def delete_task(self):

        if self.selected_task_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a task first."
            )

            return

        confirmation = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this task?"
        )

        if not confirmation:
            return

        self.db.delete_task(
            self.selected_task_id
        )

        messagebox.showinfo(
            "Deleted",
            "Task deleted successfully!"
        )

        self.clear_form()
        self.display_tasks()

    # ========================================================
    # CLEAR FORM
    # ========================================================

    def clear_form(self):

        self.title_entry.delete(
            0,
            tk.END
        )

        self.description_entry.delete(
            0,
            tk.END
        )

        self.selected_task_id = None

        for item in self.tree.selection():
            self.tree.selection_remove(item)

    # ========================================================
    # CLOSE APPLICATION
    # ========================================================

    def close_application(self):

        self.db.close()
        self.root.destroy()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = TodoGUI(root)

    root.mainloop()