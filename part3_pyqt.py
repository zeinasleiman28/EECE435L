"""
Lab 2 - Part 3: GUI with PyQt5
School Management System

- QLineEdit forms + buttons to add students, instructors and courses
- Registration / assignment through dropdowns (QComboBox)
- Records displayed in QTableWidgets with live search
- Edit / delete records, save / load JSON, export to CSV, input validation
"""
import csv
import os
import sys

from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication, QComboBox, QFileDialog,
                             QFormLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QMainWindow, QMessageBox, QPushButton, QSplitter, QTableWidget,
                             QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget)

from part1_oop import Course, Instructor, SchoolData, Student, ValidationError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE = os.path.join(BASE_DIR, "school_data.json")
KINDS = ("student", "instructor", "course")
HEADERS = {
    "student": ["ID", "Name", "Age", "Email", "Registered Courses"],
    "instructor": ["ID", "Name", "Age", "Email", "Assigned Courses"],
    "course": ["ID", "Course Name", "Instructor", "# Students", "Enrolled Students"],
}


class SchoolWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("School Management System")
        self.resize(1200, 680)
        self.current_file = None
        self.dirty = False
        self.editing = {k: None for k in KINDS}

        self._build_menu()
        self._build_ui()
        self.school = self.load_initial_data()
        self.refresh_all()

    # ------------------------------------------------- hooks (used in Part 4)
    def load_initial_data(self):
        if os.path.exists(DEFAULT_FILE):
            try:
                school = SchoolData.load(DEFAULT_FILE)
                self.current_file = DEFAULT_FILE
                return school
            except (OSError, ValidationError) as e:
                QMessageBox.warning(self, "Load failed", str(e))
        return SchoolData()

    def on_change(self, action, obj, course=None):
        """Called after every successful change to the model.
        action: add / update / delete / enroll / unenroll."""
        self.dirty = True

    # ------------------------------------------------------------------ UI
    def _build_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")
        for text, slot, shortcut in (("&Open JSON...", self.open_file, "Ctrl+O"),
                                     ("&Save", self.save_file, "Ctrl+S"),
                                     ("Save &As...", self.save_file_as, None)):
            action = QAction(text, self, triggered=slot)
            if shortcut:
                action.setShortcut(shortcut)
            self.file_menu.addAction(action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(QAction("&Export Table to CSV...", self, triggered=self.export_csv))
        self.file_menu.addSeparator()
        self.file_menu.addAction(QAction("E&xit", self, triggered=self.close))

    def _build_ui(self):
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        self.forms = QTabWidget()
        self.forms.addTab(self._student_form(), "Student")
        self.forms.addTab(self._instructor_form(), "Instructor")
        self.forms.addTab(self._course_form(), "Course")
        splitter.addWidget(self.forms)

        right = QWidget()
        layout = QVBoxLayout(right)
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search (name, ID or course):"))
        self.search = QLineEdit(placeholderText="Type to filter...")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.refresh_tables)
        search_row.addWidget(self.search)
        layout.addLayout(search_row)

        self.tables_tabs = QTabWidget()
        self.tables = {}
        for kind, title in zip(KINDS, ("Students", "Instructors", "Courses")):
            table = QTableWidget(0, len(HEADERS[kind]))
            table.setHorizontalHeaderLabels(HEADERS[kind])
            table.setSelectionBehavior(QAbstractItemView.SelectRows)
            table.setSelectionMode(QAbstractItemView.SingleSelection)
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setAlternatingRowColors(True)
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.cellDoubleClicked.connect(lambda *_, k=kind: self.edit_selected(k))
            self.tables[kind] = table
            self.tables_tabs.addTab(table, title)
        layout.addWidget(self.tables_tabs)

        buttons = QHBoxLayout()
        for text, slot in (("Edit Selected", self.edit_selected),
                           ("Delete Selected", self.delete_selected),
                           ("Export to CSV", self.export_csv)):
            button = QPushButton(text)
            button.clicked.connect(lambda _, s=slot: s())
            buttons.addWidget(button)
        buttons.addStretch()
        layout.addLayout(buttons)
        splitter.addWidget(right)
        splitter.setSizes([360, 840])

    @staticmethod
    def _person_fields(id_label):
        fields = {
            "name": QLineEdit(placeholderText="Full name", maxLength=100),
            "age": QLineEdit(placeholderText="e.g. 20"),
            "email": QLineEdit(placeholderText="name@example.com", maxLength=100),
            "id": QLineEdit(placeholderText=id_label),
        }
        fields["age"].setValidator(QIntValidator(0, 150))
        fields["id"].setValidator(QRegExpValidator(QRegExp(r"[A-Za-z0-9_-]{1,20}")))
        return fields

    def _form_box(self, title, fields, labels, save_slot, kind):
        box = QGroupBox(title)
        form = QFormLayout(box)
        for key, label in labels:
            form.addRow(label, fields[key])
        save = QPushButton(f"Add {kind.capitalize()}")
        save.clicked.connect(save_slot)
        clear = QPushButton("Clear")
        clear.clicked.connect(lambda: self.clear_form(kind))
        row = QHBoxLayout()
        row.addWidget(save)
        row.addWidget(clear)
        form.addRow(row)
        return box, save

    @staticmethod
    def _relation_box(title, person_label, buttons):
        box = QGroupBox(title)
        form = QFormLayout(box)
        person, course = QComboBox(), QComboBox()
        form.addRow(person_label, person)
        form.addRow("Course:", course)
        row = QHBoxLayout()
        for text, slot in buttons:
            button = QPushButton(text)
            button.clicked.connect(slot)
            row.addWidget(button)
        form.addRow(row)
        return box, person, course

    def _student_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.s_fields = self._person_fields("e.g. S001")
        box, self.s_save = self._form_box(
            "Student Details", self.s_fields,
            [("name", "Name:"), ("age", "Age:"), ("email", "Email:"), ("id", "Student ID:")],
            self.save_student, "student")
        layout.addWidget(box)
        box, self.reg_student, self.reg_course = self._relation_box(
            "Course Registration", "Student:",
            [("Register", self.register_course), ("Drop", self.drop_course)])
        layout.addWidget(box)
        layout.addStretch()
        return page

    def _instructor_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.i_fields = self._person_fields("e.g. I001")
        box, self.i_save = self._form_box(
            "Instructor Details", self.i_fields,
            [("name", "Name:"), ("age", "Age:"), ("email", "Email:"), ("id", "Instructor ID:")],
            self.save_instructor, "instructor")
        layout.addWidget(box)
        box, self.asg_instructor, self.asg_course = self._relation_box(
            "Course Assignment", "Instructor:",
            [("Assign", self.assign_course), ("Unassign", self.unassign_course)])
        layout.addWidget(box)
        layout.addStretch()
        return page

    def _course_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.c_fields = {
            "id": QLineEdit(placeholderText="e.g. EECE435"),
            "name": QLineEdit(placeholderText="Course name", maxLength=100),
            "instructor": QComboBox(),
        }
        self.c_fields["id"].setValidator(QRegExpValidator(QRegExp(r"[A-Za-z0-9_-]{1,20}")))
        box, self.c_save = self._form_box(
            "Course Details", self.c_fields,
            [("id", "Course ID:"), ("name", "Course Name:"), ("instructor", "Instructor:")],
            self.save_course, "course")
        layout.addWidget(box)
        layout.addStretch()
        return page

    # ------------------------------------------------------------- refresh
    def refresh_all(self):
        self.refresh_tables()
        self.refresh_combos()
        self.update_title()

    def update_title(self):
        name = os.path.basename(self.current_file) if self.current_file else "unsaved"
        self.setWindowTitle(f"School Management System - {name}{' *' if self.dirty else ''}")

    def refresh_tables(self):
        results = self.school.search(self.search.text())
        rows = {
            "student": [[s.student_id, s.name, s.age, s.email,
                         ", ".join(c.course_id for c in s.registered_courses)]
                        for s in results["students"]],
            "instructor": [[i.instructor_id, i.name, i.age, i.email,
                            ", ".join(c.course_id for c in i.assigned_courses)]
                           for i in results["instructors"]],
            "course": [[c.course_id, c.course_name, c.instructor.name if c.instructor else "",
                        len(c.enrolled_students), ", ".join(s.name for s in c.enrolled_students)]
                       for c in results["courses"]],
        }
        for kind, table in self.tables.items():
            table.setRowCount(len(rows[kind]))
            for r, row in enumerate(rows[kind]):
                for col, value in enumerate(row):
                    table.setItem(r, col, QTableWidgetItem(str(value)))
        self.statusBar().showMessage(
            f"{len(rows['student'])} students · {len(rows['instructor'])} instructors · "
            f"{len(rows['course'])} courses")

    @staticmethod
    def _fill_combo(combo, items, placeholder):
        previous = combo.currentData()
        combo.clear()
        combo.addItem(placeholder, None)
        for key, text in items:
            combo.addItem(text, key)
        index = combo.findData(previous)
        combo.setCurrentIndex(index if index >= 0 else 0)

    def refresh_combos(self):
        students = [(s.student_id, f"{s.student_id} - {s.name}") for s in self.school.students.values()]
        instructors = [(i.instructor_id, f"{i.instructor_id} - {i.name}")
                       for i in self.school.instructors.values()]
        courses = [(c.course_id, str(c)) for c in self.school.courses.values()]
        self._fill_combo(self.reg_student, students, "-- select student --")
        self._fill_combo(self.reg_course, courses, "-- select course --")
        self._fill_combo(self.asg_instructor, instructors, "-- select instructor --")
        self._fill_combo(self.asg_course, courses, "-- select course --")
        self._fill_combo(self.c_fields["instructor"], instructors, "(none)")

    def changed(self, message, action, obj, course=None):
        self.on_change(action, obj, course)
        self.refresh_all()
        self.statusBar().showMessage(message, 5000)

    def error(self, message, title="Invalid input"):
        QMessageBox.warning(self, title, message)

    # ---------------------------------------------------------- add / edit
    def _save_person(self, kind, fields, cls, add, update):
        v = {k: f.text() for k, f in fields.items()}
        key = self.editing[kind]
        try:
            if key:
                obj = update(key, v["name"], v["age"], v["email"])
                action = "update"
            else:
                obj = cls(v["name"], v["age"], v["email"], v["id"])
                add(obj)
                action = "add"
        except ValidationError as e:
            self.error(str(e))
            return
        self.clear_form(kind)
        self.changed(f"{'Added' if action == 'add' else 'Updated'} {kind} {obj.key}", action, obj)

    def save_student(self):
        self._save_person("student", self.s_fields, Student,
                          self.school.add_student, self.school.update_student)

    def save_instructor(self):
        self._save_person("instructor", self.i_fields, Instructor,
                          self.school.add_instructor, self.school.update_instructor)

    def save_course(self):
        course_id, name = self.c_fields["id"].text(), self.c_fields["name"].text()
        instructor_id = self.c_fields["instructor"].currentData()
        try:
            if self.editing["course"]:
                course = self.school.update_course(self.editing["course"], name, instructor_id)
                action = "update"
            else:
                course = Course(course_id, name)
                self.school.add_course(course)
                if instructor_id:
                    self.school.instructors[instructor_id].assign_course(course)
                action = "add"
        except ValidationError as e:
            self.error(str(e))
            return
        self.clear_form("course")
        self.changed(f"{'Added' if action == 'add' else 'Updated'} course {course.course_id}",
                     action, course)

    def _form(self, kind):
        return {"student": (self.s_fields, self.s_save), "instructor": (self.i_fields, self.i_save),
                "course": (self.c_fields, self.c_save)}[kind]

    def clear_form(self, kind):
        fields, button = self._form(kind)
        for widget in fields.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            else:
                widget.setCurrentIndex(0)
        fields["id"].setReadOnly(False)
        button.setText(f"Add {kind.capitalize()}")
        self.editing[kind] = None

    def _selected_key(self, kind):
        table = self.tables[kind]
        rows = table.selectionModel().selectedRows()
        return table.item(rows[0].row(), 0).text() if rows else None

    def edit_selected(self, kind=None):
        kind = kind or KINDS[self.tables_tabs.currentIndex()]
        key = self._selected_key(kind)
        if not key:
            self.error(f"Select a {kind} in the table first.", "Edit")
            return
        self.clear_form(kind)
        fields, button = self._form(kind)
        if kind == "course":
            course = self.school.courses[key]
            fields["name"].setText(course.course_name)
            combo = fields["instructor"]
            combo.setCurrentIndex(max(0, combo.findData(
                course.instructor.instructor_id if course.instructor else None)))
        else:
            person = getattr(self.school, f"{kind}s")[key]
            fields["name"].setText(person.name)
            fields["age"].setText(str(person.age))
            fields["email"].setText(person.email)
        fields["id"].setText(key)
        fields["id"].setReadOnly(True)  # IDs are keys; they stay fixed
        button.setText("Save Changes")
        self.editing[kind] = key
        self.forms.setCurrentIndex(KINDS.index(kind))

    def delete_selected(self):
        kind = KINDS[self.tables_tabs.currentIndex()]
        key = self._selected_key(kind)
        if not key:
            self.error(f"Select a {kind} in the table first.", "Delete")
            return
        if QMessageBox.question(self, "Delete", f"Delete {kind} '{key}'?") != QMessageBox.Yes:
            return
        obj = getattr(self.school, f"remove_{kind}")(key)
        if self.editing[kind] == key:
            self.clear_form(kind)
        self.changed(f"Deleted {kind} {key}", "delete", obj)

    # ------------------------------------------- registration / assignment
    def _pick(self, person_combo, course_combo, people, label):
        person_id, course_id = person_combo.currentData(), course_combo.currentData()
        if not person_id or not course_id:
            self.error(f"Choose a {label} and a course.", "Missing selection")
            return None, None
        return people[person_id], self.school.courses[course_id]

    def _relate(self, func, message, action, obj, course):
        try:
            func()
        except ValidationError as e:
            self.error(str(e), "Not possible")
            return
        self.changed(message, action, obj, course)

    def register_course(self):
        s, c = self._pick(self.reg_student, self.reg_course, self.school.students, "student")
        if s:
            self._relate(lambda: s.register_course(c), f"{s.name} registered in {c.course_id}",
                         "enroll", s, c)

    def drop_course(self):
        s, c = self._pick(self.reg_student, self.reg_course, self.school.students, "student")
        if s:
            self._relate(lambda: s.drop_course(c), f"{s.name} dropped {c.course_id}",
                         "unenroll", s, c)

    def assign_course(self):
        i, c = self._pick(self.asg_instructor, self.asg_course, self.school.instructors, "instructor")
        if i:  # assignment changes the course's instructor -> a course update
            self._relate(lambda: i.assign_course(c), f"{c.course_id} assigned to {i.name}",
                         "update", c, None)

    def unassign_course(self):
        i, c = self._pick(self.asg_instructor, self.asg_course, self.school.instructors, "instructor")
        if i:
            self._relate(lambda: i.unassign_course(c), f"{c.course_id} unassigned from {i.name}",
                         "update", c, None)

    # ------------------------------------------------------- files / CSV
    def _confirm_discard(self):
        return not self.dirty or QMessageBox.question(
            self, "Unsaved changes", "Discard unsaved changes?") == QMessageBox.Yes

    def open_file(self):
        if not self._confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(self, "Open data", BASE_DIR, "JSON files (*.json)")
        if not path:
            return
        try:
            self.school = SchoolData.load(path)
        except (OSError, ValidationError) as e:
            self.error(str(e), "Load failed")
            return
        self.current_file, self.dirty = path, False
        for kind in KINDS:
            self.clear_form(kind)
        self.refresh_all()

    def save_file(self):
        if self.current_file:
            self._save_to(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save data", os.path.join(BASE_DIR, "school_data.json"),
                                              "JSON files (*.json)")
        if path:
            self._save_to(path)

    def _save_to(self, path):
        try:
            self.school.save(path)
        except OSError as e:
            self.error(str(e), "Save failed")
            return
        self.current_file, self.dirty = path, False
        self.update_title()
        self.statusBar().showMessage(f"Saved to {path}", 5000)

    def export_csv(self):
        kind = KINDS[self.tables_tabs.currentIndex()]
        default = os.path.join(BASE_DIR, f"{kind}s.csv")
        path, _ = QFileDialog.getSaveFileName(self, f"Export {kind}s to CSV", default, "CSV files (*.csv)")
        if path:
            self.write_csv(kind, path)
            self.statusBar().showMessage(f"Exported {kind}s to {path}", 5000)

    def write_csv(self, kind, path):
        table = self.tables[kind]
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(HEADERS[kind])
                for r in range(table.rowCount()):
                    writer.writerow(table.item(r, c).text() for c in range(table.columnCount()))
        except OSError as e:
            self.error(str(e), "Export failed")

    def closeEvent(self, event):
        if self.dirty:
            answer = QMessageBox.question(self, "Unsaved changes", "Save before exiting?",
                                          QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if answer == QMessageBox.Cancel:
                event.ignore()
                return
            if answer == QMessageBox.Yes:
                self.save_file()
                if self.dirty:
                    event.ignore()
                    return
        event.accept()


def main(window_class=SchoolWindow):
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = window_class()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
