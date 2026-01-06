"""Domänenobjekte für die Todo-App."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from model.constants import DEFAULT_PRIORITY


@dataclass(frozen=True)
class Task:
    """Repräsentiert eine Aufgabe in der Todo-Liste."""

    id: int
    title: str
    done: bool = False
    due_date: date | None = None
    category: str | None = None
    priority: str = DEFAULT_PRIORITY
