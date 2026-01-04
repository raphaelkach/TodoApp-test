from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    done: bool = False
    due_date: date | None = None
    category: str | None = None
