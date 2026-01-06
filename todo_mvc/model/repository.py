"""Repository für den Datenzugriff auf Tasks und Kategorien."""

from __future__ import annotations

from datetime import date
from typing import List, MutableMapping

from model.entities import Task
from model.constants import (
    TASKS_KEY,
    NEXT_ID_KEY,
    CATEGORIES_KEY,
    MAX_CATEGORIES,
)


class SessionStateTaskRepository:
    """Repository zur Verwaltung von Tasks im Streamlit Session State."""

    def __init__(self, state: MutableMapping) -> None:
        self._state = state

    def ensure_initialized(self) -> None:
        """Initialisiert den Session State falls nötig."""
        if TASKS_KEY not in self._state:
            self._state[TASKS_KEY] = []
        if NEXT_ID_KEY not in self._state:
            self._state[NEXT_ID_KEY] = 1
        if CATEGORIES_KEY not in self._state:
            self._state[CATEGORIES_KEY] = []

    # ---------- Tasks ----------

    def list_all(self) -> List[Task]:
        """Gibt alle Tasks zurück."""
        self.ensure_initialized()
        return list(self._state[TASKS_KEY])

    def next_id(self) -> int:
        """Generiert die nächste eindeutige Task-ID."""
        self.ensure_initialized()
        nid = int(self._state[NEXT_ID_KEY])
        self._state[NEXT_ID_KEY] = nid + 1
        return nid

    def add(self, task: Task) -> None:
        """Fügt einen neuen Task hinzu."""
        self.ensure_initialized()
        self._state[TASKS_KEY].append(task)

    def delete(self, task_id: int) -> None:
        """Löscht einen Task anhand der ID."""
        self.ensure_initialized()
        self._state[TASKS_KEY] = [
            t for t in self._state[TASKS_KEY] if t.id != task_id
        ]

    def update(self, task_id: int, **kwargs) -> None:
        """Aktualisiert einen Task mit den gegebenen Attributen."""
        self.ensure_initialized()
        self._state[TASKS_KEY] = [
            Task(
                id=t.id,
                title=kwargs.get("title", t.title),
                done=kwargs.get("done", t.done),
                due_date=kwargs.get("due_date", t.due_date),
                category=kwargs.get("category", t.category),
                priority=kwargs.get("priority", t.priority),
            )
            if t.id == task_id
            else t
            for t in self._state[TASKS_KEY]
        ]

    # ---------- Categories ----------

    def list_categories(self) -> List[str]:
        """Gibt alle Kategorien zurück."""
        self.ensure_initialized()
        return list(self._state[CATEGORIES_KEY])

    def add_category(self, name: str) -> bool:
        """Fügt eine neue Kategorie hinzu. Gibt True zurück bei Erfolg."""
        self.ensure_initialized()
        name = (name or "").strip()
        if not name:
            return False

        cats: list[str] = self._state[CATEGORIES_KEY]
        if len(cats) >= MAX_CATEGORIES:
            return False
        if name in cats:
            return False

        cats.append(name)
        return True

    def rename_category(self, old: str, new: str) -> bool:
        """Benennt eine Kategorie um. Gibt True zurück bei Erfolg."""
        self.ensure_initialized()
        old = (old or "").strip()
        new = (new or "").strip()
        if not old or not new:
            return False

        cats: list[str] = self._state[CATEGORIES_KEY]
        if old not in cats:
            return False
        if new in cats and new != old:
            return False

        self._state[CATEGORIES_KEY] = [new if c == old else c for c in cats]

        # Aktualisiere Kategorie in allen Tasks
        self._state[TASKS_KEY] = [
            Task(
                id=t.id,
                title=t.title,
                done=t.done,
                due_date=t.due_date,
                category=(new if t.category == old else t.category),
                priority=t.priority,
            )
            for t in self._state[TASKS_KEY]
        ]
        return True

    def delete_category(self, name: str) -> bool:
        """Löscht eine Kategorie. Gibt True zurück bei Erfolg."""
        self.ensure_initialized()
        name = (name or "").strip()
        if not name:
            return False

        cats: list[str] = self._state[CATEGORIES_KEY]
        if name not in cats:
            return False

        self._state[CATEGORIES_KEY] = [c for c in cats if c != name]

        # Entferne Kategorie aus allen Tasks
        self._state[TASKS_KEY] = [
            Task(
                id=t.id,
                title=t.title,
                done=t.done,
                due_date=t.due_date,
                category=(None if t.category == name else t.category),
                priority=t.priority,
            )
            for t in self._state[TASKS_KEY]
        ]
        return True
