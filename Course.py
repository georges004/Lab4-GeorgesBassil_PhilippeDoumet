"""
Course entity (standalone model used by the GUI for validation).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import re

_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


@dataclass(frozen=True)
class Course:
    """
    Immutable view/validator for a course record.

    :param course_id: Unique course identifier (1–64 chars; letters, digits, ``._-``).
    :type course_id: str
    :param course_name: Human-readable course title (non-empty).
    :type course_name: str
    :param instructor_id: Optional instructor id who teaches the course.
    :type instructor_id: Optional[str]
    :raises ValueError: If any field fails validation rules.

    Example::

        c = Course("EECE435L", "Software Tools", "I_42")
    """

    course_id: str
    course_name: str
    instructor_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.course_id, str) or not _ID_RE.match(self.course_id):
            raise ValueError("course_id must be 1–64 chars from [A-Za-z0-9._-]")
        if not isinstance(self.course_name, str) or not self.course_name.strip():
            raise ValueError("course_name must be a non-empty string")
        if self.instructor_id is not None:
            if not isinstance(self.instructor_id, str) or not _ID_RE.match(self.instructor_id):
                raise ValueError("instructor_id must be 1–64 chars from [A-Za-z0-9._-]")

    # ---- helpers ---------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Serialize to a plain dictionary.

        :return: ``{'course_id': ..., 'course_name': ..., 'instructor_id': ...}``
        :rtype: dict
        """
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "instructor_id": self.instructor_id,
        }
