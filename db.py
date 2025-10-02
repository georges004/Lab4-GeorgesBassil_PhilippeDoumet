"""
SQLite CRUD layer for the School Management System.

This module owns the database schema and provides high-level operations used by
the PyQt GUI. All functions either return dictionaries/lists of dictionaries
(for read APIs) or perform mutations and return ``None`` (for write APIs).
"""

import sqlite3
import shutil
from typing import List, Dict, Optional

_DB_FILE = "school.db"


# ---------------------------------------------------------------------------
# internal helpers
# ---------------------------------------------------------------------------

def _get_conn() -> sqlite3.Connection:
    """Open a new SQLite connection to the shared DB file."""
    return sqlite3.connect(_DB_FILE)


# ---------------------------------------------------------------------------
# schema management
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create tables if they do not exist and ensure indices are present."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS instructors (
            instructor_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            instructor_id TEXT,
            FOREIGN KEY(instructor_id) REFERENCES instructors(instructor_id)
        );

        CREATE TABLE IF NOT EXISTS registrations (
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            PRIMARY KEY(student_id, course_id),
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(course_id) REFERENCES courses(course_id)
        );
        """
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# list helpers
# ---------------------------------------------------------------------------

def list_students() -> List[Dict]:
    """
    Return all students.

    :return: List of dicts with keys: ``student_id``, ``name``, ``age``, ``email``.
    """
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM students ORDER BY student_id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_instructors() -> List[Dict]:
    """
    Return all instructors.

    :return: List of dicts with keys: ``instructor_id``, ``name``, ``age``, ``email``.
    """
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM instructors ORDER BY instructor_id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_courses() -> List[Dict]:
    """
    Return all courses.

    :return: List of dicts with keys: ``course_id``, ``course_name``, ``instructor_id`` (or ``None``).
    """
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM courses ORDER BY course_id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# relation helpers
# ---------------------------------------------------------------------------

def student_courses(student_id: str) -> List[str]:
    """
    Return course_ids a student is enrolled in.

    :param student_id: Student primary key.
    :return: List of course_ids.
    """
    conn = _get_conn()
    rows = conn.execute(
        "SELECT course_id FROM registrations WHERE student_id=?", (student_id,)
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def instructor_courses(instructor_id: str) -> List[str]:
    """
    Return course_ids taught by an instructor.

    :param instructor_id: Instructor primary key.
    :return: List of course_ids.
    """
    conn = _get_conn()
    rows = conn.execute(
        "SELECT course_id FROM courses WHERE instructor_id=?", (instructor_id,)
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def course_students(course_id: str) -> List[str]:
    """
    Return student_ids registered to a course.

    :param course_id: Course primary key.
    :return: List of student_ids.
    """
    conn = _get_conn()
    rows = conn.execute(
        "SELECT student_id FROM registrations WHERE course_id=?", (course_id,)
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


# ---------------------------------------------------------------------------
# student CRUD
# ---------------------------------------------------------------------------

def add_student(student_id: str, name: str, age: int, email: str) -> None:
    """Insert a student row; raise on duplicate primary key or invalid input."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO students(student_id, name, age, email) VALUES (?, ?, ?, ?)",
        (student_id, name, age, email),
    )
    conn.commit()
    conn.close()


def update_student(student_id: str, name: str, age: int, email: str) -> None:
    """Update a student by id; raise if the id does not exist."""
    conn = _get_conn()
    conn.execute(
        "UPDATE students SET name=?, age=?, email=? WHERE student_id=?",
        (name, age, email, student_id),
    )
    conn.commit()
    conn.close()


def delete_student(student_id: str) -> None:
    """Delete a student and dependent registrations."""
    conn = _get_conn()
    conn.execute("DELETE FROM registrations WHERE student_id=?", (student_id,))
    conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# instructor CRUD
# ---------------------------------------------------------------------------

def add_instructor(instructor_id: str, name: str, age: int, email: str) -> None:
    """Insert an instructor row; raise on duplicate primary key or invalid input."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO instructors(instructor_id, name, age, email) VALUES (?, ?, ?, ?)",
        (instructor_id, name, age, email),
    )
    conn.commit()
    conn.close()


def update_instructor(instructor_id: str, name: str, age: int, email: str) -> None:
    """Update an instructor by id; raise if the id does not exist."""
    conn = _get_conn()
    conn.execute(
        "UPDATE instructors SET name=?, age=?, email=? WHERE instructor_id=?",
        (name, age, email, instructor_id),
    )
    conn.commit()
    conn.close()


def delete_instructor(instructor_id: str) -> None:
    """Delete an instructor and unassign from courses."""
    conn = _get_conn()
    conn.execute("UPDATE courses SET instructor_id=NULL WHERE instructor_id=?", (instructor_id,))
    conn.execute("DELETE FROM instructors WHERE instructor_id=?", (instructor_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# course CRUD
# ---------------------------------------------------------------------------

def add_course(course_id: str, course_name: str, instructor_id: Optional[str]) -> None:
    """Insert a course row; ``instructor_id`` may be ``None``."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO courses(course_id, course_name, instructor_id) VALUES (?, ?, ?)",
        (course_id, course_name, instructor_id),
    )
    conn.commit()
    conn.close()


def update_course(course_id: str, course_name: str, instructor_id: Optional[str]) -> None:
    """Update a course by id; raise if the id does not exist."""
    conn = _get_conn()
    conn.execute(
        "UPDATE courses SET course_name=?, instructor_id=? WHERE course_id=?",
        (course_name, instructor_id, course_id),
    )
    conn.commit()
    conn.close()


def delete_course(course_id: str) -> None:
    """Delete a course and its registrations."""
    conn = _get_conn()
    conn.execute("DELETE FROM registrations WHERE course_id=?", (course_id,))
    conn.execute("DELETE FROM courses WHERE course_id=?", (course_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# relations (write)
# ---------------------------------------------------------------------------

def enroll_student(student_id: str, course_id: str) -> None:
    """Create or upsert a student→course registration."""
    conn = _get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO registrations(student_id, course_id) VALUES (?, ?)",
        (student_id, course_id),
    )
    conn.commit()
    conn.close()


def assign_instructor(course_id: str, instructor_id: str) -> None:
    """Assign an instructor to teach a course (overwrites any prior assignment)."""
    conn = _get_conn()
    conn.execute(
        "UPDATE courses SET instructor_id=? WHERE course_id=?",
        (instructor_id, course_id),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# backup
# ---------------------------------------------------------------------------

def backup_db(target_path: str) -> None:
    """
    Copy the active SQLite database file to ``target_path``.

    :param target_path: Destination path (``.db`` file).
    """
    shutil.copyfile(_DB_FILE, target_path)
