"""
Student entity (inherits from :class:`Person.Person`).

Only performs **validation** and **lightweight serialization**. Persistence is
handled elsewhere (e.g., your :mod:`db` module).
"""

from __future__ import annotations
from dataclasses import dataclass
import re

from Person import Person

_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


@dataclass(frozen=True)
class Student(Person):
    """
    Immutable view/validator for a student record.

    :param name: Full name.
    :type name: str
    :param age: Age in years (0–120).
    :type age: int
    :param email: Contact email.
    :type email: str
    :param student_id: Unique student identifier (1–64 chars; letters, digits, ``._-``).
    :type student_id: str
    :raises ValueError: If any field fails validation rules.

    Example::

        s = Student("Maya", 20, "maya@uni.edu", "S-1001")
    """

    student_id: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.student_id, str) or not _ID_RE.match(self.student_id):
            raise ValueError("student_id must be 1–64 chars from [A-Za-z0-9._-]")

    # ---- helpers ---------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Serialize to a plain dictionary.

        :return: ``{'student_id': ..., 'name': ..., 'age': ..., 'email': ...}``
        :rtype: dict
        """
        base = super().to_dict()
        base.update({"student_id": self.student_id})
        return base
