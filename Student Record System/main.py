import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class StudentDatabase:
    """Handles all database operations."""

    def __init__(self, database="students.db"):
        self.database = database
        self.connection = sqlite3.connect(self.database)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_table()

    def create_table(self):
        """Create the students table and indexes."""

        query = """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            course TEXT NOT NULL,
            semester INTEGER NOT NULL,
            marks REAL DEFAULT 0
        )
        """

        self.connection.execute(query)

        # Indexes improve search performance.
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_student_name "
            "ON students(name)"
        )

        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_student_course "
            "ON students(course)"
        )

        self.connection.commit()

    # -----------------------------
    # CREATE
    # -----------------------------

    def add_student(
        self,
        roll_no,
        name,
        email,
        phone,
        course,
        semester,
        marks
    ):
        query = """
        INSERT INTO students
        (roll_no, name, email, phone, course, semester, marks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        try:
            self.connection.execute(
                query,
                (
                    roll_no,
                    name,
                    email,
                    phone,
                    course,
                    semester,
                    marks
                )
            )

            self.connection.commit()
            return True

        except sqlite3.IntegrityError:
            return False

    # -----------------------------
    # READ
    # -----------------------------

    def get_students(self):
        query = """
        SELECT id, roll_no, name, email, phone,
               course, semester, marks
        FROM students
        ORDER BY id DESC
        """

        cursor = self.connection.execute(query)
        return cursor.fetchall()

    def search_students(self, keyword):
        query = """
        SELECT id, roll_no, name, email, phone,
               course, semester, marks
        FROM students
        WHERE roll_no LIKE ?
           OR name LIKE ?
           OR email LIKE ?
           OR course LIKE ?
        ORDER BY name
        """

        search_value = f"%{keyword}%"

        cursor = self.connection.execute(
            query,
            (
                search_value,
                search_value,
                search_value,
                search_value
            )
        )

        return cursor.fetchall()

    # -----------------------------
    # UPDATE
    # -----------------------------

    def update_student(
        self,
        student_id,
        roll_no,
        name,
        email,
        phone,
        course,
        semester,
        marks
    ):
        query = """
        UPDATE students
        SET roll_no = ?,
            name = ?,
            email = ?,
            phone = ?,
            course = ?,
            semester = ?,
            marks = ?
        WHERE id = ?
        """

        try:
            self.connection.execute(
                query,
                (
                    roll_no,
                    name,
                    email,
                    phone,
                    course,
                    semester,
                    marks,
                    student_id
                )
            )

            self.connection.commit()
            return True

        except sqlite3.IntegrityError:
            return False

    # -----------------------------
    # DELETE
    # -----------------------------

    def delete_student(self, student_id):
        query = "DELETE FROM students WHERE id = ?"

        self.connection.execute(query, (student_id,))
        self.connection.commit()

    # -----------------------------
    # COUNT
    # -----------------------------

    def count_students(self):
        cursor = self.connection.execute(
            "SELECT COUNT(*) FROM students"
        )

        return cursor.fetchone()[0]

    def close(self):
        self.connection.close()


class StudentRecordApp:

    def __init__(self, root):
        self.root = root

        self.root.title("Student Record Management System")
        self.root.geometry("1150x700")
        self.root.minsize(950, 600)

        self.database = StudentDatabase()

        self.selected_student_id = None

        self.setup_style()
        self.create_interface()
        self.load_students()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

    # ==========================================
    # STYLE
    # ==========================================

    def setup_style(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 22, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=30
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold")
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=7
        )

    # ==========================================
    # INTERFACE
    # ==========================================

    def create_interface(self):

        # Main container
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        # --------------------------------------
        # Header
        # --------------------------------------

        header = ttk.Frame(main_frame)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header,
            text="Student Record Management System",
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Manage student information using a scalable SQLite database",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(3, 0))

        # --------------------------------------
        # Form
        # --------------------------------------

        form_frame = ttk.LabelFrame(
            main_frame,
            text="Student Information",
            padding=15
        )

        form_frame.pack(fill="x", pady=(0, 10))

        # Variables

        self.roll_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.course_var = tk.StringVar()
        self.semester_var = tk.StringVar()
        self.marks_var = tk.StringVar()

        # Row 1

        ttk.Label(
            form_frame,
            text="Roll No."
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)

        ttk.Entry(
            form_frame,
            textvariable=self.roll_var,
            width=25
        ).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(
            form_frame,
            text="Name"
        ).grid(row=0, column=2, sticky="w", padx=5)

        ttk.Entry(
            form_frame,
            textvariable=self.name_var,
            width=25
        ).grid(row=0, column=3, padx=5)

        ttk.Label(
            form_frame,
            text="Email"
        ).grid(row=0, column=4, sticky="w", padx=5)

        ttk.Entry(
            form_frame,
            textvariable=self.email_var,
            width=30
        ).grid(row=0, column=5, padx=5)

        # Row 2

        ttk.Label(
            form_frame,
            text="Phone"
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)

        ttk.Entry(
            form_frame,
            textvariable=self.phone_var,
            width=25
        ).grid(row=1, column=1, padx=5)

        ttk.Label(
            form_frame,
            text="Course"
        ).grid(row=1, column=2, sticky="w", padx=5)

        course_box = ttk.Combobox(
            form_frame,
            textvariable=self.course_var,
            values=[
                "MCA",
                "BCA",
                "B.Sc",
                "B.Tech",
                "M.Tech",
                "MBA",
                "Other"
            ],
            width=23,
            state="normal"
        )

        course_box.grid(row=1, column=3, padx=5)

        ttk.Label(
            form_frame,
            text="Semester"
        ).grid(row=1, column=4, sticky="w", padx=5)

        semester_box = ttk.Combobox(
            form_frame,
            textvariable=self.semester_var,
            values=[1, 2, 3, 4, 5, 6, 7, 8],
            width=27,
            state="readonly"
        )

        semester_box.grid(row=1, column=5, padx=5)

        # Row 3

        ttk.Label(
            form_frame,
            text="Marks"
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)

        ttk.Entry(
            form_frame,
            textvariable=self.marks_var,
            width=25
        ).grid(row=2, column=1, padx=5)

        # Buttons

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(
            row=2,
            column=2,
            columnspan=4,
            sticky="e",
            pady=8
        )

        ttk.Button(
            button_frame,
            text="Add Student",
            command=self.add_student
        ).pack(side="left", padx=4)

        ttk.Button(
            button_frame,
            text="Update",
            command=self.update_student
        ).pack(side="left", padx=4)

        ttk.Button(
            button_frame,
            text="Delete",
            command=self.delete_student
        ).pack(side="left", padx=4)

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_form
        ).pack(side="left", padx=4)

        # --------------------------------------
        # Search
        # --------------------------------------

        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill="x", pady=5)

        ttk.Label(
            search_frame,
            text="Search:"
        ).pack(side="left", padx=(0, 5))

        self.search_var = tk.StringVar()

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=40
        )

        search_entry.pack(side="left")

        search_entry.bind(
            "<KeyRelease>",
            self.search_students
        )

        ttk.Button(
            search_frame,
            text="Refresh",
            command=self.load_students
        ).pack(side="left", padx=5)

        # --------------------------------------
        # Table
        # --------------------------------------

        table_frame = ttk.Frame(main_frame)
        table_frame.pack(
            fill="both",
            expand=True,
            pady=(10, 5)
        )

        columns = (
            "ID",
            "Roll No",
            "Name",
            "Email",
            "Phone",
            "Course",
            "Semester",
            "Marks"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        widths = {
            "ID": 50,
            "Roll No": 100,
            "Name": 170,
            "Email": 220,
            "Phone": 120,
            "Course": 100,
            "Semester": 80,
            "Marks": 80
        }

        for column in columns:

            self.tree.heading(
                column,
                text=column
            )

            self.tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        # Scrollbars

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_student
        )

        # --------------------------------------
        # Status Bar
        # --------------------------------------

        self.status_var = tk.StringVar()

        ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w"
        ).pack(
            fill="x",
            pady=(5, 0)
        )

    # ==========================================
    # VALIDATION
    # ==========================================

    def validate_form(self):

        roll_no = self.roll_var.get().strip()
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()
        course = self.course_var.get().strip()
        semester = self.semester_var.get().strip()
        marks = self.marks_var.get().strip()

        if not roll_no:
            messagebox.showwarning(
                "Validation Error",
                "Roll number is required."
            )
            return None

        if not name:
            messagebox.showwarning(
                "Validation Error",
                "Student name is required."
            )
            return None

        if not email or "@" not in email:
            messagebox.showwarning(
                "Validation Error",
                "Enter a valid email address."
            )
            return None

        if not course:
            messagebox.showwarning(
                "Validation Error",
                "Course is required."
            )
            return None

        try:
            semester_value = int(semester)

            if not 1 <= semester_value <= 8:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Validation Error",
                "Semester must be between 1 and 8."
            )
            return None

        try:
            marks_value = float(marks)

            if not 0 <= marks_value <= 100:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Validation Error",
                "Marks must be between 0 and 100."
            )
            return None

        return (
            roll_no,
            name,
            email,
            phone,
            course,
            semester_value,
            marks_value
        )

    # ==========================================
    # CREATE
    # ==========================================

    def add_student(self):

        data = self.validate_form()

        if data is None:
            return

        success = self.database.add_student(*data)

        if success:

            messagebox.showinfo(
                "Success",
                "Student added successfully."
            )

            self.clear_form()
            self.load_students()

        else:

            messagebox.showerror(
                "Error",
                "Roll number already exists."
            )

    # ==========================================
    # READ
    # ==========================================

    def load_students(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        students = self.database.get_students()

        for student in students:
            self.tree.insert(
                "",
                "end",
                values=student
            )

        self.status_var.set(
            f"Total Students: {len(students)}"
        )

    # ==========================================
    # SEARCH
    # ==========================================

    def search_students(self, event=None):

        keyword = self.search_var.get().strip()

        if not keyword:
            self.load_students()
            return

        students = self.database.search_students(keyword)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for student in students:
            self.tree.insert(
                "",
                "end",
                values=student
            )

        self.status_var.set(
            f"Search Results: {len(students)}"
        )

    # ==========================================
    # SELECT
    # ==========================================

    def select_student(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(
            selected[0],
            "values"
        )

        if not values:
            return

        self.selected_student_id = values[0]

        self.roll_var.set(values[1])
        self.name_var.set(values[2])
        self.email_var.set(values[3])
        self.phone_var.set(values[4])
        self.course_var.set(values[5])
        self.semester_var.set(values[6])
        self.marks_var.set(values[7])

    # ==========================================
    # UPDATE
    # ==========================================

    def update_student(self):

        if self.selected_student_id is None:

            messagebox.showwarning(
                "Update",
                "Select a student from the table first."
            )

            return

        data = self.validate_form()

        if data is None:
            return

        success = self.database.update_student(
            self.selected_student_id,
            *data
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Student record updated successfully."
            )

            self.clear_form()
            self.load_students()

        else:

            messagebox.showerror(
                "Error",
                "Roll number already belongs to another student."
            )

    # ==========================================
    # DELETE
    # ==========================================

    def delete_student(self):

        if self.selected_student_id is None:

            messagebox.showwarning(
                "Delete",
                "Select a student from the table first."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this student?"
        )

        if not confirm:
            return

        self.database.delete_student(
            self.selected_student_id
        )

        messagebox.showinfo(
            "Success",
            "Student deleted successfully."
        )

        self.clear_form()
        self.load_students()

    # ==========================================
    # CLEAR
    # ==========================================

    def clear_form(self):

        self.selected_student_id = None

        self.roll_var.set("")
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.course_var.set("")
        self.semester_var.set("")
        self.marks_var.set("")

        for item in self.tree.selection():
            self.tree.selection_remove(item)

    # ==========================================
    # CLOSE
    # ==========================================

    def close_application(self):

        self.database.close()
        self.root.destroy()


# ==============================================
# APPLICATION START
# ==============================================

if __name__ == "__main__":

    root = tk.Tk()

    app = StudentRecordApp(root)

    root.mainloop()