"""
School Management System GUI (PyQt5 + SQLite)

This module provides a desktop GUI to manage students, instructors and courses,
with CRUD operations backed by a lightweight SQLite layer in :mod:`db`.

Run this file directly to launch the app::

    python main_window_PyQt_db.py

The UI contains:
- A global search field (filters all tables as you type)
- Forms to add students, instructors, and courses
- Registration (student→course) and assignment (instructor→course)
- Three data tables with select→edit behavior
- CSV export and DB backup utilities
"""

import sys, csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

# Domain classes (used here for validation only)
from Student import Student
from Instructor import Instructor
from Course import Course

# SQLite CRUD layer
import db


class MainWindow(QMainWindow):
    """
    Main application window.

    The window wires the forms, tables, and buttons to the underlying SQLite
    CRUD functions in :mod:`db`. It also performs lightweight validation by
    instantiating :class:`Student`, :class:`Instructor`, and :class:`Course`.

    The lifecycle after construction is:

    1. Ensure DB schema exists via :func:`db.init_db`.
    2. Build the UI widgets and layouts.
    3. Populate combo boxes and tables via :meth:`refresh_all`.
    """

    def __init__(self):
        """Create the main window, initialize the DB, build the UI, and load data."""
        super().__init__()
        self.setWindowTitle("School Management System (SQLite)")
        self.resize(1100, 820)

        db.init_db()  # ensure tables exist

        self._build_ui()
        self.refresh_all()

    # ---------- helpers ----------
    def refresh_all(self):
        """Refresh all dynamic UI elements (combos and tables)."""
        self._refresh_combos()
        self._fill_tables()

    def _refresh_combos(self):
        """Reload the items of all combo boxes from the database."""
        self.instructor_for_course.clear()
        self.instructor_for_course.addItem("")  # optional
        for i in db.list_instructors():
            self.instructor_for_course.addItem(f"{i['instructor_id']} - {i['name']}")

        self.reg_student_combo.clear()
        for s in db.list_students():
            self.reg_student_combo.addItem(f"{s['student_id']} - {s['name']}")

        self.reg_course_combo.clear()
        for c in db.list_courses():
            self.reg_course_combo.addItem(f"{c['course_id']} - {c['course_name']}")

        self.assign_instr_combo.clear()
        for i in db.list_instructors():
            self.assign_instr_combo.addItem(f"{i['instructor_id']} - {i['name']}")

        self.assign_course_combo.clear()
        for c in db.list_courses():
            self.assign_course_combo.addItem(f"{c['course_id']} - {c['course_name']}")

    def _fill_tables(self, term: str = ""):
        """
        Fill all three tables (students, instructors, courses).

        :param term: Case-insensitive filter text; if present, only rows whose
                     concatenated fields contain this text are shown.
        """
        t = term.lower().strip()

        # Students
        srows = []
        for s in db.list_students():
            courses_str = ", ".join(db.student_courses(s["student_id"]))
            hay = f"{s['student_id']} {s['name']} {s['age']} {s['email']} {courses_str}".lower()
            if t in hay:
                srows.append((s["student_id"], s["name"], str(s["age"]), s["email"], courses_str))
        self._fill_table(self.students_table, srows)

        # Instructors
        irows = []
        for ins in db.list_instructors():
            courses_str = ", ".join(db.instructor_courses(ins["instructor_id"]))
            hay = f"{ins['instructor_id']} {ins['name']} {ins['age']} {ins['email']} {courses_str}".lower()
            if t in hay:
                irows.append((ins["instructor_id"], ins["name"], str(ins["age"]), ins["email"], courses_str))
        self._fill_table(self.instructors_table, irows)

        # Courses
        crows = []
        for c in db.list_courses():
            instr_id = c["instructor_id"] or ""
            roster = ", ".join(db.course_students(c["course_id"]))
            hay = f"{c['course_id']} {c['course_name']} {instr_id} {roster}".lower()
            if t in hay:
                crows.append((c["course_id"], c["course_name"], instr_id, roster))
        self._fill_table(self.courses_table, crows)

    def _fill_table(self, table, rows):
        """
        Populate a ``QTableWidget`` with rows.

        :param table: Target table.
        :type table: QTableWidget
        :param rows: Iterable of tuples of strings (one tuple per row).
        """
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(val)
                if c == 0:
                    # Keep ID visually read-only; edits should go through forms.
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                table.setItem(r, c, item)
        table.resizeColumnsToContents()

    # ---------- UI ----------
    def _build_ui(self):
        """Create all widgets, layouts, signals, and set the central widget."""
        root = QWidget()
        outer = QVBoxLayout(root)

        # top bar: search + CSV + backup + reload
        top = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name, ID, or course…")
        self.search_edit.textChanged.connect(lambda: self._fill_tables(self.search_edit.text()))
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(lambda: (self.search_edit.clear(), self._fill_tables("")))
        btn_export = QPushButton("Export CSV…")
        btn_export.clicked.connect(self.export_csv)
        btn_backup = QPushButton("Backup DB…")
        btn_backup.clicked.connect(self.backup_db)
        btn_reload = QPushButton("Reload")
        btn_reload.clicked.connect(self.refresh_all)

        top.addWidget(QLabel("Search:"))
        top.addWidget(self.search_edit)
        top.addWidget(btn_clear)
        top.addStretch(1)
        top.addWidget(btn_export)
        top.addWidget(btn_backup)
        top.addWidget(btn_reload)
        outer.addLayout(top)

        # forms row: Student + Instructor
        forms_row = QHBoxLayout()
        forms_row.addWidget(self._student_form())
        forms_row.addWidget(self._instructor_form())
        outer.addLayout(forms_row)

        # course form (full width)
        outer.addWidget(self._course_form())

        # registration row
        reg_row = QHBoxLayout()
        reg_row.addWidget(self._student_registration_box())
        reg_row.addWidget(self._instructor_assignment_box())
        outer.addLayout(reg_row)

        # tables + bottom actions
        outer.addWidget(self._tables_box())
        outer.addLayout(self._bottom_actions())

        self.setCentralWidget(root)

    def _student_form(self):
        """Create and return the 'Add Student' group box."""
        box = QGroupBox("Add Student")
        g = QGridLayout(box)

        self.stu_name = QLineEdit()
        self.stu_age = QLineEdit()
        self.stu_email = QLineEdit()
        self.stu_id = QLineEdit()

        g.addWidget(QLabel("Name"), 0, 0); g.addWidget(self.stu_name, 0, 1)
        g.addWidget(QLabel("Age"), 1, 0); g.addWidget(self.stu_age, 1, 1)
        g.addWidget(QLabel("Email"), 2, 0); g.addWidget(self.stu_email, 2, 1)
        g.addWidget(QLabel("Student ID"), 3, 0); g.addWidget(self.stu_id, 3, 1)

        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.add_student)
        g.addWidget(btn_add, 4, 0, 1, 2)
        return box

    def _instructor_form(self):
        """Create and return the 'Add Instructor' group box."""
        box = QGroupBox("Add Instructor")
        g = QGridLayout(box)

        self.ins_name = QLineEdit()
        self.ins_age = QLineEdit()
        self.ins_email = QLineEdit()
        self.ins_id = QLineEdit()

        g.addWidget(QLabel("Name"), 0, 0); g.addWidget(self.ins_name, 0, 1)
        g.addWidget(QLabel("Age"), 1, 0); g.addWidget(self.ins_age, 1, 1)
        g.addWidget(QLabel("Email"), 2, 0); g.addWidget(self.ins_email, 2, 1)
        g.addWidget(QLabel("Instructor ID"), 3, 0); g.addWidget(self.ins_id, 3, 1)

        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.add_instructor)
        g.addWidget(btn_add, 4, 0, 1, 2)
        return box

    def _course_form(self):
        """Create and return the 'Add Course' group box."""
        box = QGroupBox("Add Course")
        g = QGridLayout(box)

        self.course_id_edit = QLineEdit()
        self.course_name_edit = QLineEdit()
        self.instructor_for_course = QComboBox()

        g.addWidget(QLabel("Course ID"), 0, 0); g.addWidget(self.course_id_edit, 0, 1)
        g.addWidget(QLabel("Course Name"), 1, 0); g.addWidget(self.course_name_edit, 1, 1)
        g.addWidget(QLabel("Instructor (optional)"), 2, 0); g.addWidget(self.instructor_for_course, 2, 1)

        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.add_course)
        g.addWidget(btn_add, 3, 0, 1, 2)
        return box

    def _student_registration_box(self):
        """Create and return the 'Register Student to Course' group box."""
        box = QGroupBox("Register Student to Course")
        g = QGridLayout(box)
        self.reg_student_combo = QComboBox()
        self.reg_course_combo = QComboBox()
        g.addWidget(QLabel("Student"), 0, 0); g.addWidget(self.reg_student_combo, 0, 1)
        g.addWidget(QLabel("Course"), 1, 0); g.addWidget(self.reg_course_combo, 1, 1)
        btn = QPushButton("Register")
        btn.clicked.connect(self.register_student)
        g.addWidget(btn, 2, 0, 1, 2)
        return box

    def _instructor_assignment_box(self):
        """Create and return the 'Assign Instructor to Course' group box."""
        box = QGroupBox("Assign Instructor to Course")
        g = QGridLayout(box)
        self.assign_instr_combo = QComboBox()
        self.assign_course_combo = QComboBox()
        g.addWidget(QLabel("Instructor"), 0, 0); g.addWidget(self.assign_instr_combo, 0, 1)
        g.addWidget(QLabel("Course"), 1, 0); g.addWidget(self.assign_course_combo, 1, 1)
        btn = QPushButton("Assign")
        btn.clicked.connect(self.assign_instructor)
        g.addWidget(btn, 2, 0, 1, 2)
        return box

    def _tables_box(self):
        """Create the three data tables (students, instructors, courses)."""
        box = QGroupBox("Records")
        v = QVBoxLayout(box)
        self.tabs = QTabWidget()

        # students table
        self.students_table = QTableWidget(0, 5)
        self.students_table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Email", "Courses"])
        self.students_table.itemSelectionChanged.connect(self._student_row_selected)
        self.tabs.addTab(self.students_table, "Students")

        # instructors table
        self.instructors_table = QTableWidget(0, 5)
        self.instructors_table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Email", "Courses"])
        self.instructors_table.itemSelectionChanged.connect(self._instructor_row_selected)
        self.tabs.addTab(self.instructors_table, "Instructors")

        # courses table
        self.courses_table = QTableWidget(0, 4)
        self.courses_table.setHorizontalHeaderLabels(["Course ID", "Course Name", "Instructor", "Students"])
        self.courses_table.itemSelectionChanged.connect(self._course_row_selected)
        self.tabs.addTab(self.courses_table, "Courses")

        v.addWidget(self.tabs)
        return box

    def _bottom_actions(self):
        """Create the bottom action buttons (update / delete)."""
        h = QHBoxLayout()
        self.btn_update_selected = QPushButton("Update Selected")
        self.btn_delete_selected = QPushButton("Delete Selected")
        self.btn_update_selected.clicked.connect(self.update_selected)
        self.btn_delete_selected.clicked.connect(self.delete_selected)
        h.addStretch(1)
        h.addWidget(self.btn_update_selected)
        h.addWidget(self.btn_delete_selected)
        return h

    # ---------- selections fill the forms ----------
    def _student_row_selected(self):
        """When a student row is selected, populate the student form with its values."""
        sel = self.students_table.selectedItems()
        if not sel: return
        sid = self.students_table.item(sel[0].row(), 0).text()
        for s in db.list_students():
            if s["student_id"] == sid:
                self.stu_name.setText(s["name"])
                self.stu_age.setText(str(s["age"]))
                self.stu_email.setText(s["email"])
                self.stu_id.setText(s["student_id"])
                break

    def _instructor_row_selected(self):
        """When an instructor row is selected, populate the instructor form with its values."""
        sel = self.instructors_table.selectedItems()
        if not sel: return
        iid = self.instructors_table.item(sel[0].row(), 0).text()
        for i in db.list_instructors():
            if i["instructor_id"] == iid:
                self.ins_name.setText(i["name"])
                self.ins_age.setText(str(i["age"]))
                self.ins_email.setText(i["email"])
                self.ins_id.setText(i["instructor_id"])
                break

    def _course_row_selected(self):
        """When a course row is selected, populate the course form with its values."""
        sel = self.courses_table.selectedItems()
        if not sel: return
        cid = self.courses_table.item(sel[0].row(), 0).text()
        for c in db.list_courses():
            if c["course_id"] == cid:
                self.course_id_edit.setText(c["course_id"])
                self.course_name_edit.setText(c["course_name"])
                if c["instructor_id"]:
                    for ins in db.list_instructors():
                        if ins["instructor_id"] == c["instructor_id"]:
                            self.instructor_for_course.setCurrentText(f"{ins['instructor_id']} - {ins['name']}")
                            break
                else:
                    self.instructor_for_course.setCurrentText("")
                break

    # ---------- add / update / delete ----------
    def add_student(self):
        """Validate and add a new student using :func:`db.add_student`, then refresh UI."""
        try:
            name = self.stu_name.text().strip()
            age = int(self.stu_age.text().strip())
            email = self.stu_email.text().strip()
            sid = self.stu_id.text().strip()
            Student(name, age, email, sid)  # validation
            db.add_student(sid, name, age, email)
            self.stu_name.clear(); self.stu_age.clear(); self.stu_email.clear(); self.stu_id.clear()
            self.refresh_all()
            QMessageBox.information(self, "OK", "Student added.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_instructor(self):
        """Validate and add a new instructor using :func:`db.add_instructor`, then refresh UI."""
        try:
            name = self.ins_name.text().strip()
            age = int(self.ins_age.text().strip())
            email = self.ins_email.text().strip()
            iid = self.ins_id.text().strip()
            Instructor(name, age, email, iid)  # validation
            db.add_instructor(iid, name, age, email)
            self.ins_name.clear(); self.ins_age.clear(); self.ins_email.clear(); self.ins_id.clear()
            self.refresh_all()
            QMessageBox.information(self, "OK", "Instructor added.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_course(self):
        """Validate and add a new course using :func:`db.add_course`, then refresh UI."""
        try:
            cid = self.course_id_edit.text().strip()
            cname = self.course_name_edit.text().strip()
            text = self.instructor_for_course.currentText().strip()
            instr_id = text.split(" - ", 1)[0] if text else None
            Course(cid, cname, None)  # basic validation
            db.add_course(cid, cname, instr_id)
            self.course_id_edit.clear(); self.course_name_edit.clear(); self.instructor_for_course.setCurrentText("")
            self.refresh_all()
            QMessageBox.information(self, "OK", "Course added.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_selected(self):
        """Update whichever record is selected in the current tab (student/instructor/course)."""
        tab = self.tabs.currentIndex()
        try:
            if tab == 0:
                sel = self.students_table.selectedItems()
                if not sel: raise ValueError("select a student row")
                sid = self.students_table.item(sel[0].row(), 0).text()
                name = self.stu_name.text().strip()
                age = int(self.stu_age.text().strip())
                email = self.stu_email.text().strip()
                Student(name, age, email, sid)
                db.update_student(sid, name, age, email)

            elif tab == 1:
                sel = self.instructors_table.selectedItems()
                if not sel: raise ValueError("select an instructor row")
                iid = self.instructors_table.item(sel[0].row(), 0).text()
                name = self.ins_name.text().strip()
                age = int(self.ins_age.text().strip())
                email = self.ins_email.text().strip()
                Instructor(name, age, email, iid)
                db.update_instructor(iid, name, age, email)

            else:
                sel = self.courses_table.selectedItems()
                if not sel: raise ValueError("select a course row")
                cid = self.courses_table.item(sel[0].row(), 0).text()
                cname = self.course_name_edit.text().strip()
                text = self.instructor_for_course.currentText().strip()
                instr_id = text.split(" - ", 1)[0] if text else None
                Course(cid, cname, None)
                db.update_course(cid, cname, instr_id)

            self.refresh_all()
            QMessageBox.information(self, "OK", "Record updated.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected(self):
        """Delete the selected record in the active tab via the appropriate :mod:`db` function."""
        tab = self.tabs.currentIndex()
        try:
            if tab == 0:
                sel = self.students_table.selectedItems()
                if not sel: raise ValueError("select a student row")
                sid = self.students_table.item(sel[0].row(), 0).text()
                db.delete_student(sid)

            elif tab == 1:
                sel = self.instructors_table.selectedItems()
                if not sel: raise ValueError("select an instructor row")
                iid = self.instructors_table.item(sel[0].row(), 0).text()
                db.delete_instructor(iid)

            else:
                sel = self.courses_table.selectedItems()
                if not sel: raise ValueError("select a course row")
                cid = self.courses_table.item(sel[0].row(), 0).text()
                db.delete_course(cid)

            self.refresh_all()
            QMessageBox.information(self, "OK", "Record deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ---------- registration & assignment ----------
    def register_student(self):
        """Register the selected student into the selected course via :func:`db.enroll_student`."""
        try:
            s_text = self.reg_student_combo.currentText().strip()
            c_text = self.reg_course_combo.currentText().strip()
            if not s_text or not c_text:
                raise ValueError("select a student and a course")
            sid = s_text.split(" - ", 1)[0]
            cid = c_text.split(" - ", 1)[0]
            db.enroll_student(sid, cid)
            self.refresh_all()
            QMessageBox.information(self, "OK", "Student registered to course.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def assign_instructor(self):
        """Assign the selected instructor to the selected course via :func:`db.assign_instructor`."""
        try:
            i_text = self.assign_instr_combo.currentText().strip()
            c_text = self.assign_course_combo.currentText().strip()
            if not i_text or not c_text:
                raise ValueError("select an instructor and a course")
            iid = i_text.split(" - ", 1)[0]
            cid = c_text.split(" - ", 1)[0]
            db.assign_instructor(cid, iid)
            self.refresh_all()
            QMessageBox.information(self, "OK", "Instructor assigned to course.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ---------- export & backup ----------
    def export_csv(self):
        """Export the current tab’s records to a CSV file chosen by the user."""
        tab = self.tabs.currentIndex()
        default_name = ["students.csv", "instructors.csv", "courses.csv"][tab]
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", default_name, "CSV (*.csv)")
        if not path: return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                if tab == 0:
                    w.writerow(["student_id", "name", "age", "email", "courses"])
                    for s in db.list_students():
                        w.writerow([s["student_id"], s["name"], s["age"], s["email"],
                                    ";".join(db.student_courses(s["student_id"]))])
                elif tab == 1:
                    w.writerow(["instructor_id", "name", "age", "email", "courses"])
                    for i in db.list_instructors():
                        w.writerow([i["instructor_id"], i["name"], i["age"], i["email"],
                                    ";".join(db.instructor_courses(i["instructor_id"]))])
                else:
                    w.writerow(["course_id", "course_name", "instructor_id", "students"])
                    for c in db.list_courses():
                        w.writerow([c["course_id"], c["course_name"], c["instructor_id"] or "",
                                    ";".join(db.course_students(c["course_id"]))])
            QMessageBox.information(self, "Exported", f"CSV exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def backup_db(self):
        """Copy the active SQLite database file to a user-chosen path via :func:`db.backup_db`."""
        path, _ = QFileDialog.getSaveFileName(self, "Backup SQLite DB", "school_backup.db", "SQLite DB (*.db)")
        if not path: return
        try:
            db.backup_db(path)
            QMessageBox.information(self, "Backup", f"Database backed up to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
