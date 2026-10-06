"""
Lab 2 - Part 4: Database Integration (data layer)
School Management System

- Schema for students, instructors, courses and enrollments (SQLite)
- CRUD operations using parameterized queries (no SQL injection)
- Backup and restore of the whole database
Run this file directly for a small command-line demo.
"""
import logging
import os
import shutil
import sqlite3
from datetime import datetime

from part1_oop import (Course, Instructor, SchoolData, Student, validate_age, validate_email,
                       validate_id, validate_text)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "school.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

logging.basicConfig(filename=os.path.join(BASE_DIR, "app.log"), level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("school")

SCHEMA = """
CREATE TABLE IF NOT EXISTS instructors (
    instructor_id TEXT PRIMARY KEY,
    name          TEXT    NOT NULL,
    age           INTEGER NOT NULL CHECK (age >= 0),
    email         TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name       TEXT    NOT NULL,
    age        INTEGER NOT NULL CHECK (age >= 0),
    email      TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS courses (
    course_id     TEXT PRIMARY KEY,
    course_name   TEXT NOT NULL,
    instructor_id TEXT REFERENCES instructors(instructor_id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS enrollments (
    student_id  TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id   TEXT NOT NULL REFERENCES courses(course_id)   ON DELETE CASCADE,
    enrolled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id)
);
"""
TABLES = {"students", "instructors", "courses", "enrollments"}


class SchoolDatabase:
    def __init__(self, path=DB_FILE):
        self.path = path
        self.conn = self._connect(path)
        self.conn.executescript(SCHEMA)

    @staticmethod
    def _connect(path):
        conn = sqlite3.connect(path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _write(self, query, params=()):
        with self.conn:  # commits on success, rolls back on error
            cur = self.conn.execute(query, params)
        log.info("%s %s", query.split()[0].upper(), params)
        return cur.rowcount

    def _rows(self, query, params=()):
        return self.conn.execute(query, params).fetchall()

    # ------------------------------------------------------------ students
    def insert_student(self, student_id, name, age, email):
        self._write("INSERT INTO students VALUES (?, ?, ?, ?)",
                    (validate_id(student_id), validate_text(name, "Name"),
                     validate_age(age), validate_email(email)))

    def get_students(self):
        return self._rows("SELECT student_id, name, age, email FROM students ORDER BY student_id")

    def update_student(self, student_id, name, age, email):
        return self._write("UPDATE students SET name=?, age=?, email=? WHERE student_id=?",
                           (validate_text(name, "Name"), validate_age(age),
                            validate_email(email), student_id))

    def delete_student(self, student_id):
        return self._write("DELETE FROM students WHERE student_id=?", (student_id,))

    # --------------------------------------------------------- instructors
    def insert_instructor(self, instructor_id, name, age, email):
        self._write("INSERT INTO instructors VALUES (?, ?, ?, ?)",
                    (validate_id(instructor_id), validate_text(name, "Name"),
                     validate_age(age), validate_email(email)))

    def get_instructors(self):
        return self._rows("SELECT instructor_id, name, age, email FROM instructors "
                          "ORDER BY instructor_id")

    def update_instructor(self, instructor_id, name, age, email):
        return self._write("UPDATE instructors SET name=?, age=?, email=? WHERE instructor_id=?",
                           (validate_text(name, "Name"), validate_age(age),
                            validate_email(email), instructor_id))

    def delete_instructor(self, instructor_id):
        return self._write("DELETE FROM instructors WHERE instructor_id=?", (instructor_id,))

    # ------------------------------------------------------------- courses
    def insert_course(self, course_id, course_name, instructor_id=None):
        self._write("INSERT INTO courses VALUES (?, ?, ?)",
                    (validate_id(course_id), validate_text(course_name, "Course name"),
                     instructor_id))

    def get_courses(self):
        return self._rows("SELECT course_id, course_name, instructor_id FROM courses "
                          "ORDER BY course_id")

    def update_course(self, course_id, course_name, instructor_id=None):
        return self._write("UPDATE courses SET course_name=?, instructor_id=? WHERE course_id=?",
                           (validate_text(course_name, "Course name"), instructor_id, course_id))

    def delete_course(self, course_id):
        return self._write("DELETE FROM courses WHERE course_id=?", (course_id,))

    # --------------------------------------------------------- enrollments
    def enroll(self, student_id, course_id):
        self._write("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
                    (student_id, course_id))

    def unenroll(self, student_id, course_id):
        return self._write("DELETE FROM enrollments WHERE student_id=? AND course_id=?",
                           (student_id, course_id))

    def get_enrollments(self):
        return self._rows("SELECT student_id, course_id FROM enrollments "
                          "ORDER BY student_id, course_id")

    # ----------------------------------------- object model <-> database
    def save_object(self, obj):
        """Insert an OOP object (Part 1 classes)."""
        if isinstance(obj, Student):
            self.insert_student(obj.student_id, obj.name, obj.age, obj.email)
        elif isinstance(obj, Instructor):
            self.insert_instructor(obj.instructor_id, obj.name, obj.age, obj.email)
        elif isinstance(obj, Course):
            self.insert_course(obj.course_id, obj.course_name,
                               obj.instructor.instructor_id if obj.instructor else None)

    def update_object(self, obj):
        if isinstance(obj, Student):
            self.update_student(obj.student_id, obj.name, obj.age, obj.email)
        elif isinstance(obj, Instructor):
            self.update_instructor(obj.instructor_id, obj.name, obj.age, obj.email)
        elif isinstance(obj, Course):
            self.update_course(obj.course_id, obj.course_name,
                               obj.instructor.instructor_id if obj.instructor else None)

    def delete_object(self, obj):
        if isinstance(obj, Student):
            self.delete_student(obj.student_id)
        elif isinstance(obj, Instructor):
            self.delete_instructor(obj.instructor_id)
        elif isinstance(obj, Course):
            self.delete_course(obj.course_id)

    def load_school(self):
        """Read every table and rebuild the Part 1 object model."""
        return SchoolData.from_dict({
            "instructors": [dict(zip(("instructor_id", "name", "age", "email"), r))
                            for r in self.get_instructors()],
            "courses": [dict(zip(("course_id", "course_name", "instructor_id"), r))
                        for r in self.get_courses()],
            "students": [{**dict(zip(("student_id", "name", "age", "email"), r)),
                          "registered_courses": [c for s, c in self.get_enrollments() if s == r[0]]}
                         for r in self.get_students()],
        })

    def import_school(self, school):
        """Replace the database contents with a SchoolData object (one transaction)."""
        with self.conn:
            for table in ("enrollments", "courses", "students", "instructors"):
                self.conn.execute(f"DELETE FROM {table}")  # fixed names, not user input
            self.conn.executemany("INSERT INTO instructors VALUES (?, ?, ?, ?)",
                                  [(i.instructor_id, i.name, i.age, i.email)
                                   for i in school.instructors.values()])
            self.conn.executemany("INSERT INTO courses VALUES (?, ?, ?)",
                                  [(c.course_id, c.course_name,
                                    c.instructor.instructor_id if c.instructor else None)
                                   for c in school.courses.values()])
            self.conn.executemany("INSERT INTO students VALUES (?, ?, ?, ?)",
                                  [(s.student_id, s.name, s.age, s.email)
                                   for s in school.students.values()])
            self.conn.executemany("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
                                  [(s.student_id, c.course_id) for s in school.students.values()
                                   for c in s.registered_courses])
        log.info("IMPORT %d students, %d instructors, %d courses", len(school.students),
                 len(school.instructors), len(school.courses))

    def is_empty(self):
        return not any(self._rows(f"SELECT 1 FROM {t} LIMIT 1") for t in TABLES)

    # ---------------------------------------------------- backup / restore
    def backup(self, dest_path=None):
        """Copy the live database to a file (safe even while it is open)."""
        if dest_path is None:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = os.path.join(BACKUP_DIR, f"school_backup_{stamp}.db")
        dest = sqlite3.connect(dest_path)
        try:
            self.conn.backup(dest)
        finally:
            dest.close()
        log.info("BACKUP -> %s", dest_path)
        return dest_path

    def restore(self, src_path):
        """Replace the live database with a backup file."""
        src = sqlite3.connect(f"file:{src_path}?mode=ro", uri=True)
        try:
            found = {r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not TABLES <= found:
                raise sqlite3.DatabaseError("The selected file is not a School Management backup.")
            src.backup(self.conn)
        finally:
            src.close()
        self.conn.execute("PRAGMA foreign_keys = ON")
        log.info("RESTORE <- %s", src_path)

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    from part1_oop import build_sample_school

    demo_path = os.path.join(BASE_DIR, "demo.db")
    if os.path.exists(demo_path):
        os.remove(demo_path)
    db = SchoolDatabase(demo_path)

    db.import_school(build_sample_school())
    print("Students:   ", db.get_students())
    print("Instructors:", db.get_instructors())
    print("Courses:    ", db.get_courses())
    print("Enrollments:", db.get_enrollments())

    db.insert_student("S004", "Rami Aoun", 22, "rami.aoun@mail.aub.edu")    # Create
    db.enroll("S004", "EECE330")
    db.update_student("S004", "Rami Aoun", 23, "rami@mail.aub.edu")         # Update
    print("\nAfter insert/update S004:", db.get_students()[-1])
    backup = db.backup(os.path.join(BASE_DIR, "demo_backup.db"))           # Backup
    db.delete_instructor("I002")                                            # Delete
    print("After deleting I002, courses:", db.get_courses())
    db.restore(backup)                                                      # Restore
    print("After restore, courses:      ", db.get_courses())
    db.close()
    os.remove(demo_path)
    os.remove(backup)
