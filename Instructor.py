"""
Instructor entity (inherits from :class:`Person.Person`).
"""

from __future__ import annotations
from dataclasses import dataclass
import re

from Person import Person

_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


@dataclass(frozen=True)
class Instructor(Person):
    """
    Immutable view/validator for an instructor record.

    :param name: Full name.
    :type name: str
    :param age: Age in years (0–120).
    :type age: int
    :param email: Contact email.
    :type email: str
    :param instructor_id: Unique instructor identifier (1–64 chars; letters, digits, ``._-``).
    :type instructor_id: str
    :raises ValueError: If any field fails validation rules.

    Example::

        i = Instructor("Dr. Karim", 38, "karim@dept.edu", "I_42")
    """

    instructor_id: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.instructor_id, str) or not _ID_RE.match(self.instructor_id):
            raise ValueError("instructor_id must be 1–64 chars from [A-Za-z0-9._-]")

    # ---- helpers ---------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Serialize to a plain dictionary.

        :return: ``{'instructor_id': ..., 'name': ..., 'age': ..., 'email': ...}``
        :rtype: dict
        """
        base = super().to_dict()
        base.update({"instructor_id": self.instructor_id})
        return base
