# # Create an todo list in python with optimized code. 

# def show_tasks(tasks):
#     if not tasks:
#         print("\nNo tasks available.")
#     else:
#         print("\nTODO List:")
#         for i, task in enumerate(tasks, 1):
#             print(f"{i}. {task}")


# def main():
#     tasks = []

#     while True:
#         print("\n=== TODO MENU ===")
#         print("1. Add Task")
#         print("2. View Tasks")
#         print("3. Remove Task")
#         print("4. Exit")

#         choice = input("Enter your choice: ").strip()

#         if choice == "1":
#             task = input("Enter task: ").strip()
#             if task:
#                 tasks.append(task)
#                 print("Task added.")
#             else:
#                 print("Task cannot be empty.")

#         elif choice == "2":
#             show_tasks(tasks)

#         elif choice == "3":
#             show_tasks(tasks)
#             if tasks:
#                 try:
#                     index = int(input("Enter task number to remove: ")) - 1
#                     print(f"Removed: {tasks.pop(index)}")
#                 except (ValueError, IndexError):
#                     print("Invalid task number.")

#         elif choice == "4":
#             print("Goodbye!")
#             break

#         else:
#             print("Invalid choice. Try again.")


# if __name__ == "__main__":
#     main()
    
# Create a program using tuple that manages student records, including student names, exam scores and final grades.

# student_records = (
#     ("Alice", 85, 88),
#     ("Bob", 78, 82),
#     ("Charlie", 92, 95)
# )

# for name, exam_score, final_grade in student_records:
#     print(f"Name: {name}, Exam Score: {exam_score}, Final Grade: {final_grade}")

# Student Record Management System That manages student records, including student names, exam scores, and final grades using a dictionary.
# Take input from the user to add new student records and display all records.

# student_records = {}

# while True:
#     print("\n=== STUDENT RECORD MANAGEMENT ===")
#     print("1. Add Student Record")
#     print("2. Display All Records")
#     print("3. Exit")

#     choice = input("Enter your choice: ").strip()

#     if choice == "1":
#         name = input("Enter student name: ").strip()
#         exam_score = float(input("Enter exam score: "))
#         final_grade = float(input("Enter final grade: "))
#         student_records[name] = (exam_score, final_grade)
#         print("Student record added.")

#     elif choice == "2":
#         if not student_records:
#             print("\nNo student records available.")
#         else:
#             print("\nStudent Records:")
#             for name, (exam_score, final_grade) in student_records.items():
#                 print(f"Name: {name}, Exam Score: {exam_score}, Final Grade: {final_grade}")

#     elif choice == "3":
#         print("Goodbye!")
#         break

#     else:
#         print("Invalid choice. Try again.")
        
# GUI For Student record management system using tkinter/streamlit. 
# The GUI should allow users to add new student records, view existing records, and delete records. 
# It should also display the average exam score and final grade for all students.

import tkinter as tk
from tkinter import ttk, messagebox

# Dictionary to store records
student_records = {}

# -------------------- FUNCTIONS --------------------

def add_student():
    name = name_entry.get().strip()

    if name == "":
        messagebox.showerror("Error", "Student name cannot be empty.")
        return

    try:
        exam_score = float(exam_entry.get())
        final_grade = float(grade_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values.")
        return

    student_records[name] = (exam_score, final_grade)

    update_table()
    clear_entries()
    messagebox.showinfo("Success", "Student record added successfully.")


def delete_student():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Please select a student to delete.")
        return

    item = selected[0]
    name = tree.item(item)["values"][0]

    del student_records[name]

    update_table()
    messagebox.showinfo("Deleted", f"{name}'s record deleted.")


def update_table():
    # Clear existing rows
    for row in tree.get_children():
        tree.delete(row)

    total_exam = 0
    total_grade = 0

    # Insert updated records
    for name, (exam, grade) in student_records.items():
        tree.insert("", tk.END, values=(name, exam, grade))
        total_exam += exam
        total_grade += grade

    # Calculate averages
    if student_records:
        avg_exam = total_exam / len(student_records)
        avg_grade = total_grade / len(student_records)
    else:
        avg_exam = 0
        avg_grade = 0

    avg_exam_label.config(text=f"Average Exam Score: {avg_exam:.2f}")
    avg_grade_label.config(text=f"Average Final Grade: {avg_grade:.2f}")


def clear_entries():
    name_entry.delete(0, tk.END)
    exam_entry.delete(0, tk.END)
    grade_entry.delete(0, tk.END)


# -------------------- GUI --------------------

root = tk.Tk()
root.title("Student Record Management System")
root.geometry("700x500")
root.resizable(False, False)

# Title
title = tk.Label(root,
                 text="Student Record Management System",
                 font=("Arial", 18, "bold"))
title.pack(pady=10)

# Input Frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Student Name").grid(row=0, column=0, padx=5, pady=5)
name_entry = tk.Entry(input_frame, width=20)
name_entry.grid(row=0, column=1)

tk.Label(input_frame, text="Exam Score").grid(row=1, column=0, padx=5, pady=5)
exam_entry = tk.Entry(input_frame, width=20)
exam_entry.grid(row=1, column=1)

tk.Label(input_frame, text="Final Grade").grid(row=2, column=0, padx=5, pady=5)
grade_entry = tk.Entry(input_frame, width=20)
grade_entry.grid(row=2, column=1)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame,
          text="Add Student",
          width=15,
          command=add_student,
          bg="lightgreen").grid(row=0, column=0, padx=10)

tk.Button(button_frame,
          text="Delete Student",
          width=15,
          command=delete_student,
          bg="tomato").grid(row=0, column=1, padx=10)

# Table
columns = ("Name", "Exam Score", "Final Grade")

tree = ttk.Treeview(root, columns=columns, show="headings", height=10)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=180)

tree.pack(pady=10)

# Average Labels
avg_exam_label = tk.Label(root,
                          text="Average Exam Score: 0.00",
                          font=("Arial", 11, "bold"))

avg_exam_label.pack()

avg_grade_label = tk.Label(root,
                           text="Average Final Grade: 0.00",
                           font=("Arial", 11, "bold"))

avg_grade_label.pack(pady=5)

# Run GUI
root.mainloop()