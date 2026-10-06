"""
Lab 2 - Part 4: Database Integration (GUI)
School Management System connected to SQLite

Reuses the PyQt5 window from Part 3 through inheritance. Every add / edit /
delete / registration is written to school.db immediately (CRUD), and the
Database menu provides backup, restore and JSON import.
"""
import os
import sqlite3

from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox

from part1_oop import SchoolData, ValidationError
from part3_pyqt import BASE_DIR, DEFAULT_FILE, KINDS, SchoolWindow, main
from part4_database import BACKUP_DIR, DB_FILE, SchoolDatabase, log


class DatabaseSchoolWindow(SchoolWindow):
    def __init__(self):
        self.db = SchoolDatabase(DB_FILE)  # must exist before the base class loads data
        super().__init__()

    # ---------------------------------------- overridden hooks from Part 3
    def load_initial_data(self):
        if self.db.is_empty() and os.path.exists(DEFAULT_FILE):
            try:  # first run: seed the database from the Part 1 sample data
                self.db.import_school(SchoolData.load(DEFAULT_FILE))
            except (OSError, ValidationError, sqlite3.Error) as e:
                QMessageBox.warning(self, "Import failed", str(e))
        return self.db.load_school()

    def on_change(self, action, obj, course=None):
        try:
            if action == "add":
                self.db.save_object(obj)
            elif action == "update":
                self.db.update_object(obj)
            elif action == "delete":
                self.db.delete_object(obj)
            elif action == "enroll":
                self.db.enroll(obj.student_id, course.course_id)
            elif action == "unenroll":
                self.db.unenroll(obj.student_id, course.course_id)
        except (sqlite3.Error, ValidationError) as e:
            log.error("Database error on %s %r: %s", action, obj, e)
            QMessageBox.critical(self, "Database error", f"The change was not saved:\n{e}")
            self.reload_from_db()  # keep the screen in sync with what is stored

    def update_title(self):
        self.setWindowTitle(f"School Management System - SQLite ({os.path.basename(self.db.path)})")

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(QAction("&Export Table to CSV...", self, triggered=self.export_csv))
        file_menu.addSeparator()
        file_menu.addAction(QAction("E&xit", self, triggered=self.close))

        db_menu = self.menuBar().addMenu("&Database")
        db_menu.addAction(QAction("&Backup Now", self, triggered=self.quick_backup))
        db_menu.addAction(QAction("Backup &As...", self, triggered=self.backup_as))
        db_menu.addAction(QAction("&Restore from Backup...", self, triggered=self.restore_backup))
        db_menu.addSeparator()
        db_menu.addAction(QAction("&Import JSON (replace all)...", self, triggered=self.import_json))
        db_menu.addAction(QAction("Re&load", self, triggered=self.reload_from_db))

    # --------------------------------------------------------- DB actions
    def reload_from_db(self):
        self.school = self.db.load_school()
        for kind in KINDS:
            self.clear_form(kind)
        self.refresh_all()

    def quick_backup(self):
        try:
            path = self.db.backup()
        except (OSError, sqlite3.Error) as e:
            self.error(str(e), "Backup failed")
            return
        QMessageBox.information(self, "Backup", f"Database backed up to:\n{path}")

    def backup_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Backup database",
                                              os.path.join(BASE_DIR, "school_backup.db"),
                                              "SQLite database (*.db)")
        if not path:
            return
        if os.path.abspath(path) == os.path.abspath(self.db.path):
            self.error("Choose a file other than the live database.", "Backup")
            return
        try:
            self.db.backup(path)
        except (OSError, sqlite3.Error) as e:
            self.error(str(e), "Backup failed")
            return
        self.statusBar().showMessage(f"Backed up to {path}", 5000)

    def restore_backup(self):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        path, _ = QFileDialog.getOpenFileName(self, "Restore database", BACKUP_DIR,
                                              "SQLite database (*.db)")
        if not path:
            return
        if QMessageBox.question(self, "Restore", "Replace ALL current data with this backup?"
                                ) != QMessageBox.Yes:
            return
        try:
            self.db.restore(path)
            self.reload_from_db()
        except (sqlite3.Error, ValidationError) as e:
            self.error(str(e), "Restore failed")
            return
        self.statusBar().showMessage(f"Restored from {path}", 5000)

    def import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import JSON", BASE_DIR, "JSON files (*.json)")
        if not path:
            return
        if QMessageBox.question(self, "Import", "Replace ALL database data with this file?"
                                ) != QMessageBox.Yes:
            return
        try:
            self.db.import_school(SchoolData.load(path))
            self.reload_from_db()
        except (OSError, ValidationError, sqlite3.Error) as e:
            self.error(str(e), "Import failed")

    def closeEvent(self, event):
        self.db.close()  # every change is already committed
        event.accept()


if __name__ == "__main__":
    main(DatabaseSchoolWindow)
