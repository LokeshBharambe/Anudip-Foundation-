import sqlite3
from datetime import datetime


# ============================================================
# DATABASE LAYER
# ============================================================

class Database:
    def __init__(self, db_name="todo.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row

        # Improve SQLite performance
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute("PRAGMA synchronous = NORMAL")

        self.create_table()

    def create_table(self):
        """Create tasks table and indexes."""

        query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """

        self.connection.execute(query)

        # Indexes improve searching/filtering performance
        self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status
            ON tasks(status)
        """)

        self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_created_at
            ON tasks(created_at)
        """)

        self.connection.commit()

    def close(self):
        self.connection.close()


# ============================================================
# TODO APP
# ============================================================

class TodoApp:

    def __init__(self):
        self.db = Database()

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    def create_task(self, title, description=""):
        """Create a new task."""

        if not title.strip():
            print("❌ Task title cannot be empty.")
            return

        now = datetime.now().isoformat(timespec="seconds")

        query = """
        INSERT INTO tasks
        (title, description, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """

        self.db.connection.execute(
            query,
            (title.strip(), description.strip(), "pending", now, now)
        )

        self.db.connection.commit()

        print("✅ Task created successfully.")

    # --------------------------------------------------------
    # READ ALL
    # --------------------------------------------------------

    def get_tasks(self):
        """Display all tasks."""

        query = """
        SELECT id, title, description, status, created_at
        FROM tasks
        ORDER BY id DESC
        """

        cursor = self.db.connection.execute(query)
        tasks = cursor.fetchall()

        if not tasks:
            print("\n📭 No tasks found.")
            return

        print("\n" + "=" * 70)
        print("                    ALL TASKS")
        print("=" * 70)

        for task in tasks:
            status = "✓ Completed" if task["status"] == "completed" else "○ Pending"

            print(f"""
ID          : {task['id']}
Title       : {task['title']}
Description : {task['description']}
Status      : {status}
Created     : {task['created_at']}
{'-' * 70}
""")

    # --------------------------------------------------------
    # READ SINGLE TASK
    # --------------------------------------------------------

    def get_task(self, task_id):
        """Find and display a specific task."""

        query = """
        SELECT *
        FROM tasks
        WHERE id = ?
        """

        task = self.db.connection.execute(
            query,
            (task_id,)
        ).fetchone()

        if not task:
            print("❌ Task not found.")
            return

        print("\n" + "=" * 50)
        print("TASK DETAILS")
        print("=" * 50)

        print(f"ID          : {task['id']}")
        print(f"Title       : {task['title']}")
        print(f"Description : {task['description']}")
        print(f"Status      : {task['status']}")
        print(f"Created     : {task['created_at']}")
        print(f"Updated     : {task['updated_at']}")

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update_task(self, task_id, title=None, description=None):
        """Update an existing task."""

        # Check whether task exists
        check_query = """
        SELECT id FROM tasks WHERE id = ?
        """

        task = self.db.connection.execute(
            check_query,
            (task_id,)
        ).fetchone()

        if not task:
            print("❌ Task not found.")
            return

        updates = []
        values = []

        if title is not None and title.strip():
            updates.append("title = ?")
            values.append(title.strip())

        if description is not None:
            updates.append("description = ?")
            values.append(description.strip())

        if not updates:
            print("⚠️ Nothing to update.")
            return

        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat(timespec="seconds"))

        values.append(task_id)

        query = f"""
        UPDATE tasks
        SET {", ".join(updates)}
        WHERE id = ?
        """

        self.db.connection.execute(query, values)
        self.db.connection.commit()

        print("✅ Task updated successfully.")

    # --------------------------------------------------------
    # MARK COMPLETED
    # --------------------------------------------------------

    def mark_completed(self, task_id):
        """Mark a task as completed."""

        query = """
        UPDATE tasks
        SET status = 'completed',
            updated_at = ?
        WHERE id = ?
        """

        cursor = self.db.connection.execute(
            query,
            (
                datetime.now().isoformat(timespec="seconds"),
                task_id
            )
        )

        self.db.connection.commit()

        if cursor.rowcount == 0:
            print("❌ Task not found.")
        else:
            print("✅ Task marked as completed.")

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def delete_task(self, task_id):
        """Delete a task."""

        query = """
        DELETE FROM tasks
        WHERE id = ?
        """

        cursor = self.db.connection.execute(
            query,
            (task_id,)
        )

        self.db.connection.commit()

        if cursor.rowcount == 0:
            print("❌ Task not found.")
        else:
            print("🗑️ Task deleted successfully.")

    # --------------------------------------------------------
    # CLOSE APPLICATION
    # --------------------------------------------------------

    def close(self):
        self.db.close()


# ============================================================
# USER INTERFACE
# ============================================================

def main():

    app = TodoApp()

    while True:

        print("\n")
        print("=" * 50)
        print("             📝 TO-DO APPLICATION")
        print("=" * 50)

        print("1. Create Task")
        print("2. View All Tasks")
        print("3. View Single Task")
        print("4. Update Task")
        print("5. Mark Task Completed")
        print("6. Delete Task")
        print("7. Exit")

        print("=" * 50)

        choice = input("Enter your choice: ").strip()

        # CREATE
        if choice == "1":

            title = input("Enter task title: ")
            description = input("Enter description: ")

            app.create_task(title, description)

        # READ ALL
        elif choice == "2":

            app.get_tasks()

        # READ SINGLE
        elif choice == "3":

            try:
                task_id = int(input("Enter task ID: "))
                app.get_task(task_id)

            except ValueError:
                print("❌ Please enter a valid ID.")

        # UPDATE
        elif choice == "4":

            try:
                task_id = int(input("Enter task ID: "))

                title = input(
                    "Enter new title (press Enter to keep current): "
                )

                description = input(
                    "Enter new description (press Enter to keep current): "
                )

                title = title if title else None
                description = description if description else None

                app.update_task(
                    task_id,
                    title,
                    description
                )

            except ValueError:
                print("❌ Please enter a valid ID.")

        # COMPLETE
        elif choice == "5":

            try:
                task_id = int(input("Enter task ID: "))
                app.mark_completed(task_id)

            except ValueError:
                print("❌ Please enter a valid ID.")

        # DELETE
        elif choice == "6":

            try:
                task_id = int(input("Enter task ID: "))
                app.delete_task(task_id)

            except ValueError:
                print("❌ Please enter a valid ID.")

        # EXIT
        elif choice == "7":

            app.close()
            print("\n👋 Thank you for using the To-Do App!")
            break

        else:
            print("❌ Invalid choice. Please try again.")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()