# Lab 2 – School Management System

Requirements: Python 3, Tkinter (included with Python), PyQt5 (`pip install PyQt5`).

| Part | File | Run |
|---|---|---|
| 1 – OOP classes, validation, JSON save/load | `part1_oop.py` | `python part1_oop.py` (also creates `school_data.json` sample data) |
| 2 – Tkinter GUI | `part2_tkinter.py` | `python part2_tkinter.py` |
| 3 – PyQt5 GUI | `part3_pyqt.py` | `python part3_pyqt.py` |
| 4 – SQLite data layer (CRUD, backup/restore) | `part4_database.py` | `python part4_database.py` (command-line demo) |
| 4 – PyQt5 GUI connected to SQLite | `part4_app.py` | `python part4_app.py` |

Run Part 1 first so the GUIs open with sample data. The first time Part 4 runs, it copies that data into `school.db`.

## Features
- **OOP:** `Person` → `Student` / `Instructor` (inheritance), with `introduce()` overridden in each (polymorphism). Attributes are validated properties such as `_email` (encapsulation), and every class derives from an abstract `Entity` base (abstraction).
- **Validation:** non-empty name, age a whole number from 0 to 150, valid email format, IDs without spaces, no duplicate IDs.
- **GUIs:** add forms, register/drop courses and assign/unassign instructors from dropdowns, search by name, ID or course, edit (double-click a row or *Edit Selected*), delete, and save/load JSON.
  - The PyQt version can also export the shown table to CSV.
- **Database:** tables `students`, `instructors`, `courses` and `enrollments`, with foreign keys:
  - Deleting a student or course removes its enrollments.
  - Deleting an instructor leaves their courses without an instructor.
  - Every change in the Part 4 GUI is saved right away, and all queries are parameterized.
  - The *Database* menu has Backup Now (saved in `backups/`), Backup As, Restore, and Import JSON.
  - Actions are logged to `app.log`.
