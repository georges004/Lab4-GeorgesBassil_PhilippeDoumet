"""
Base person entity used for validation and data transfer.

This module defines :class:`Person`, a minimal immutable model with common
fields shared by students and instructors.

Typical usage::

    from Person import Person
    p = Person(name="Alice", age=21, email="alice@example.com")
"""

from __future__ import annotations
from dataclasses import dataclass
import re


_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$")


@dataclass(frozen=True)
class Person:
    """
    Immutable person.

    :param name: Full name (non-empty).
    :type name: str
    :param age: Age in years (0–120).
    :type age: int
    :param email: Contact email (basic RFC-5322 style check).
    :type email: str
    :raises ValueError: If any field fails validation.
    """

    name: str
    age: int
    email: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(self.age, int) or not (0 <= self.age <= 120):
            raise ValueError("age must be an integer in [0, 120]")
        if not isinstance(self.email, str) or not _EMAIL_RE.match(self.email):
            raise ValueError("email is not a valid email address")

    # ---- helpers ---------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Serialize to a plain dictionary.

        :return: ``{'name': ..., 'age': ..., 'email': ...}``
        :rtype: dict
        """
        return {"name": self.name, "age": self.age, "email": self.email}
