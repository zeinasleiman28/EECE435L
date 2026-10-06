"""
Lab 2 - Part 2: GUI with Tkinter
School Management System

- Forms (entries + buttons) to add students, instructors and courses
- Course registration / instructor assignment through dropdowns (ttk.Combobox)
- All records shown in Treeviews, with search by name, ID or course
- Edit / delete records, save / load data to / from a JSON file
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from part1_oop import Course, Instructor, SchoolData, Student, ValidationError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE = os.path.join(BASE_DIR, "school_data.json")

COLUMNS = {
    "student": ("ID", "Name", "Age", "Email", "Registered Courses"),
    "instructor": ("ID", "Name", "Age", "Email", "Assigned Courses"),
    "course": ("ID", "Course Name", "Instructor", "# Students", "Enrolled Students"),
}


def id_of(choice):
    """Combobox items look like 'S001 - Lina Khoury'; IDs contain no spaces."""
    return choice.split(" - ", 1)[0] if choice else ""


class SchoolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("School Management System")
        self.geometry("1150x640")
        self.minsize(980, 560)

        self.school = SchoolData()
        self.current_file = None
        self.dirty = False
        self.editing = {"student": None, "instructor": None, "course": None}

        self._build_menu()
        self._build_layout()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        if os.path.exists(DEFAULT_FILE):
            self._load_from(DEFAULT_FILE)
        self.refresh_all()

    # ------------------------------------------------------------------ UI
    def _build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)
        self.bind_all("<Control-o>", lambda e: self.open_file())
        self.bind_all("<Control-s>", lambda e: self.save_file())

    def _build_layout(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.forms = ttk.Notebook(paned)
        self._build_student_tab()
        self._build_instructor_tab()
        self._build_course_tab()
        paned.add(self.forms, weight=1)

        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        search_bar = ttk.Frame(right)
        search_bar.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(search_bar, text="Search (name, ID or course):").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_trees())
        ttk.Entry(search_bar, textvariable=self.search_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        ttk.Button(search_bar, text="Clear", command=lambda: self.search_var.set("")).pack(side=tk.LEFT)

        self.records = ttk.Notebook(right)
        self.records.pack(fill=tk.BOTH, expand=True)
        self.trees = {}
        for kind, title in (("student", "Students"), ("instructor", "Instructors"),
                            ("course", "Courses")):
            frame = ttk.Frame(self.records)
            tree = ttk.Treeview(frame, columns=COLUMNS[kind], show="headings", selectmode="browse")
            for col in COLUMNS[kind]:
                tree.heading(col, text=col)
                tree.column(col, width=60 if col in ("Age", "# Students") else 130, anchor=tk.W)
            scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scroll.set)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scroll.pack(side=tk.RIGHT, fill=tk.Y)
            tree.bind("<Double-1>", lambda e, k=kind: self.edit_selected(k))
            self.records.add(frame, text=title)
            self.trees[kind] = tree

        actions = ttk.Frame(right)
        actions.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(actions, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT)
        ttk.Button(actions, text="Delete Selected", command=self.delete_selected).pack(
            side=tk.LEFT, padx=6)
        self.status = ttk.Label(actions, text="", foreground="gray30")
        self.status.pack(side=tk.RIGHT)

    @staticmethod
    def _entry(parent, label, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=3)
        entry = ttk.Entry(parent, width=28)
        entry.grid(row=row, column=1, sticky=tk.EW, pady=3)
        return entry

    @staticmethod
    def _combo(parent, label, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=3)
        combo = ttk.Combobox(parent, state="readonly", width=26)
        combo.grid(row=row, column=1, sticky=tk.EW, pady=3)
        return combo

    @staticmethod
    def _section(parent, text, row):
        ttk.Separator(parent).grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=10)
        ttk.Label(parent, text=text, font=("Segoe UI", 10, "bold")).grid(
            row=row + 1, column=0, columnspan=2, sticky=tk.W)

    def _person_form(self, title, id_label):
        tab = ttk.Frame(self.forms, padding=10)
        tab.columnconfigure(1, weight=1)
        self.forms.add(tab, text=title)
        fields = {
            "name": self._entry(tab, "Name:", 0),
            "age": self._entry(tab, "Age:", 1),
            "email": self._entry(tab, "Email:", 2),
            "id": self._entry(tab, id_label, 3),
        }
        return tab, fields

    def _build_student_tab(self):
        tab, self.s_fields = self._person_form("Student", "Student ID:")
        btns = ttk.Frame(tab)
        btns.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=6)
        self.s_save_btn = ttk.Button(btns, text="Add Student", command=self.save_student)
        self.s_save_btn.pack(side=tk.LEFT)
        ttk.Button(btns, text="Clear", command=lambda: self.clear_form("student")).pack(
            side=tk.LEFT, padx=6)

        self._section(tab, "Course Registration", 5)
        self.reg_student = self._combo(tab, "Student:", 7)
        self.reg_course = self._combo(tab, "Course:", 8)
        btns = ttk.Frame(tab)
        btns.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=6)
        ttk.Button(btns, text="Register", command=self.register_course).pack(side=tk.LEFT)
        ttk.Button(btns, text="Drop", command=self.drop_course).pack(side=tk.LEFT, padx=6)

    def _build_instructor_tab(self):
        tab, self.i_fields = self._person_form("Instructor", "Instructor ID:")
        btns = ttk.Frame(tab)
        btns.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=6)
        self.i_save_btn = ttk.Button(btns, text="Add Instructor", command=self.save_instructor)
        self.i_save_btn.pack(side=tk.LEFT)
        ttk.Button(btns, text="Clear", command=lambda: self.clear_form("instructor")).pack(
            side=tk.LEFT, padx=6)

        self._section(tab, "Course Assignment", 5)
        self.asg_instructor = self._combo(tab, "Instructor:", 7)
        self.asg_course = self._combo(tab, "Course:", 8)
        btns = ttk.Frame(tab)
        btns.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=6)
        ttk.Button(btns, text="Assign", command=self.assign_course).pack(side=tk.LEFT)
        ttk.Button(btns, text="Unassign", command=self.unassign_course).pack(side=tk.LEFT, padx=6)

    def _build_course_tab(self):
        tab = ttk.Frame(self.forms, padding=10)
        tab.columnconfigure(1, weight=1)
        self.forms.add(tab, text="Course")
        self.c_fields = {
            "id": self._entry(tab, "Course ID:", 0),
            "name": self._entry(tab, "Course Name:", 1),
        }
        self.c_instructor = self._combo(tab, "Instructor:", 2)
        btns = ttk.Frame(tab)
        btns.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=6)
        self.c_save_btn = ttk.Button(btns, text="Add Course", command=self.save_course)
        self.c_save_btn.pack(side=tk.LEFT)
        ttk.Button(btns, text="Clear", command=lambda: self.clear_form("course")).pack(
            side=tk.LEFT, padx=6)

    # ------------------------------------------------------------- refresh
    def refresh_all(self):
        self.refresh_trees()
        self.refresh_combos()
        name = os.path.basename(self.current_file) if self.current_file else "unsaved"
        self.title(f"School Management System - {name}{' *' if self.dirty else ''}")

    def refresh_trees(self):
        results = self.school.search(self.search_var.get())
        rows = {
            "student": [(s.student_id, s.name, s.age, s.email,
                         ", ".join(c.course_id for c in s.registered_courses))
                        for s in results["students"]],
            "instructor": [(i.instructor_id, i.name, i.age, i.email,
                            ", ".join(c.course_id for c in i.assigned_courses))
                           for i in results["instructors"]],
            "course": [(c.course_id, c.course_name, c.instructor.name if c.instructor else "",
                        len(c.enrolled_students), ", ".join(s.name for s in c.enrolled_students))
                       for c in results["courses"]],
        }
        for kind, tree in self.trees.items():
            tree.delete(*tree.get_children())
            for row in rows[kind]:
                tree.insert("", tk.END, iid=row[0], values=row)
        self.status.config(text=f"{len(rows['student'])} students · {len(rows['instructor'])} "
                                f"instructors · {len(rows['course'])} courses")

    def refresh_combos(self):
        students = [f"{s.student_id} - {s.name}" for s in self.school.students.values()]
        instructors = [f"{i.instructor_id} - {i.name}" for i in self.school.instructors.values()]
        courses = [str(c) for c in self.school.courses.values()]
        for combo, values in ((self.reg_student, students), (self.reg_course, courses),
                              (self.asg_instructor, instructors), (self.asg_course, courses),
                              (self.c_instructor, ["(none)"] + instructors)):
            combo["values"] = values
            if combo.get() not in values:  # keep the selection if it still exists
                combo.set("")

    def changed(self, message):
        self.dirty = True
        self.refresh_all()
        self.status.config(text=message)

    # ---------------------------------------------------------- add / edit
    @staticmethod
    def _values(fields):
        return {k: e.get() for k, e in fields.items()}

    def save_student(self):
        v = self._values(self.s_fields)
        try:
            if self.editing["student"]:
                s = self.school.update_student(self.editing["student"], v["name"], v["age"], v["email"])
                msg = f"Updated student {s.student_id}"
            else:
                s = Student(v["name"], v["age"], v["email"], v["id"])
                self.school.add_student(s)
                msg = f"Added student {s.student_id}"
        except ValidationError as e:
            messagebox.showerror("Invalid input", str(e), parent=self)
            return
        self.clear_form("student")
        self.changed(msg)

    def save_instructor(self):
        v = self._values(self.i_fields)
        try:
            if self.editing["instructor"]:
                i = self.school.update_instructor(
                    self.editing["instructor"], v["name"], v["age"], v["email"])
                msg = f"Updated instructor {i.instructor_id}"
            else:
                i = Instructor(v["name"], v["age"], v["email"], v["id"])
                self.school.add_instructor(i)
                msg = f"Added instructor {i.instructor_id}"
        except ValidationError as e:
            messagebox.showerror("Invalid input", str(e), parent=self)
            return
        self.clear_form("instructor")
        self.changed(msg)

    def save_course(self):
        v = self._values(self.c_fields)
        instructor_id = id_of(self.c_instructor.get()) if self.c_instructor.get() != "(none)" else ""
        try:
            if self.editing["course"]:
                c = self.school.update_course(self.editing["course"], v["name"], instructor_id or None)
                msg = f"Updated course {c.course_id}"
            else:
                c = Course(v["id"], v["name"])
                self.school.add_course(c)
                if instructor_id:
                    self.school.instructors[instructor_id].assign_course(c)
                msg = f"Added course {c.course_id}"
        except ValidationError as e:
            messagebox.showerror("Invalid input", str(e), parent=self)
            return
        self.clear_form("course")
        self.changed(msg)

    def clear_form(self, kind):
        fields = {"student": self.s_fields, "instructor": self.i_fields, "course": self.c_fields}[kind]
        fields["id"].config(state=tk.NORMAL)
        for entry in fields.values():
            entry.delete(0, tk.END)
        if kind == "course":
            self.c_instructor.set("")
        self.editing[kind] = None
        button = {"student": self.s_save_btn, "instructor": self.i_save_btn,
                  "course": self.c_save_btn}[kind]
        button.config(text=f"Add {kind.capitalize()}")

    def _selected(self, kind):
        selection = self.trees[kind].selection()
        return selection[0] if selection else None

    def _current_kind(self):
        return ("student", "instructor", "course")[self.records.index(self.records.select())]

    def edit_selected(self, kind=None):
        kind = kind or self._current_kind()
        key = self._selected(kind)
        if not key:
            messagebox.showinfo("Edit", f"Select a {kind} in the table first.", parent=self)
            return
        self.clear_form(kind)
        if kind == "course":
            c = self.school.courses[key]
            fields = self.c_fields
            values = {"id": c.course_id, "name": c.course_name}
            self.c_instructor.set(f"{c.instructor.instructor_id} - {c.instructor.name}"
                                  if c.instructor else "(none)")
        else:
            p = self.school.students[key] if kind == "student" else self.school.instructors[key]
            fields = self.s_fields if kind == "student" else self.i_fields
            values = {"name": p.name, "age": p.age, "email": p.email, "id": key}
        for name, value in values.items():
            fields[name].insert(0, value)
        fields["id"].config(state="readonly")  # IDs are keys; they stay fixed
        self.editing[kind] = key
        button = {"student": self.s_save_btn, "instructor": self.i_save_btn,
                  "course": self.c_save_btn}[kind]
        button.config(text="Save Changes")
        self.forms.select(("student", "instructor", "course").index(kind))

    def delete_selected(self):
        kind = self._current_kind()
        key = self._selected(kind)
        if not key:
            messagebox.showinfo("Delete", f"Select a {kind} in the table first.", parent=self)
            return
        if not messagebox.askyesno("Delete", f"Delete {kind} '{key}'?", parent=self):
            return
        getattr(self.school, f"remove_{kind}")(key)
        if self.editing[kind] == key:
            self.clear_form(kind)
        self.changed(f"Deleted {kind} {key}")

    # ------------------------------------------- registration / assignment
    def _pick(self, person_combo, course_combo, people, label):
        person_id, course_id = id_of(person_combo.get()), id_of(course_combo.get())
        if not person_id or not course_id:
            messagebox.showwarning("Missing selection", f"Choose a {label} and a course.", parent=self)
            return None, None
        return people[person_id], self.school.courses[course_id]

    def _relate(self, action, message):
        try:
            action()
        except ValidationError as e:
            messagebox.showwarning("Not possible", str(e), parent=self)
            return
        self.changed(message)

    def register_course(self):
        s, c = self._pick(self.reg_student, self.reg_course, self.school.students, "student")
        if s:
            self._relate(lambda: s.register_course(c), f"{s.name} registered in {c.course_id}")

    def drop_course(self):
        s, c = self._pick(self.reg_student, self.reg_course, self.school.students, "student")
        if s:
            self._relate(lambda: s.drop_course(c), f"{s.name} dropped {c.course_id}")

    def assign_course(self):
        i, c = self._pick(self.asg_instructor, self.asg_course, self.school.instructors, "instructor")
        if i:
            self._relate(lambda: i.assign_course(c), f"{c.course_id} assigned to {i.name}")

    def unassign_course(self):
        i, c = self._pick(self.asg_instructor, self.asg_course, self.school.instructors, "instructor")
        if i:
            self._relate(lambda: i.unassign_course(c), f"{c.course_id} unassigned from {i.name}")

    # ------------------------------------------------------------- files
    def _confirm_discard(self):
        return not self.dirty or messagebox.askyesno(
            "Unsaved changes", "Discard unsaved changes?", parent=self)

    def new_file(self):
        if self._confirm_discard():
            self.school, self.current_file, self.dirty = SchoolData(), None, False
            for kind in self.editing:
                self.clear_form(kind)
            self.refresh_all()

    def open_file(self):
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(parent=self, initialdir=BASE_DIR,
                                          filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if path:
            self._load_from(path)
            self.refresh_all()

    def _load_from(self, path):
        try:
            self.school = SchoolData.load(path)
        except (OSError, ValidationError) as e:
            messagebox.showerror("Load failed", f"Could not load {path}:\n{e}", parent=self)
            return
        self.current_file, self.dirty = path, False
        for kind in self.editing:
            self.clear_form(kind)

    def save_file(self):
        if self.current_file:
            self._save_to(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        path = filedialog.asksaveasfilename(parent=self, initialdir=BASE_DIR,
                                            defaultextension=".json",
                                            filetypes=[("JSON files", "*.json")])
        if path:
            self._save_to(path)

    def _save_to(self, path):
        try:
            self.school.save(path)
        except OSError as e:
            messagebox.showerror("Save failed", str(e), parent=self)
            return
        self.current_file, self.dirty = path, False
        self.refresh_all()
        self.status.config(text=f"Saved to {os.path.basename(path)}")

    def on_close(self):
        if self.dirty:
            answer = messagebox.askyesnocancel("Unsaved changes", "Save before exiting?", parent=self)
            if answer is None:
                return
            if answer:
                self.save_file()
                if self.dirty:  # save was cancelled or failed
                    return
        self.destroy()


if __name__ == "__main__":
    SchoolApp().mainloop()
