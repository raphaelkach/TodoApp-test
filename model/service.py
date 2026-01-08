"""Service-Schicht mit Geschäftslogik und Validierung."""

from __future__ import annotations

from datetime import date
from typing import List

from model.entities import Task
from model.repository import SessionStateTaskRepository
from model.constants import PRIORITIES, DEFAULT_PRIORITY


class TodoService:
    """Service für die Geschäftslogik der Todo-App."""

    def __init__(self, repo: SessionStateTaskRepository) -> None:
        self._repo = repo

    def initialize(self) -> None:
        """Initialisiert das Repository."""
        self._repo.ensure_initialized()

    # ---------- Validierung ----------

    def _validate_title(self, title: str | None) -> str | None:
        """Validiert und normalisiert einen Titel."""
        title = (title or "").strip()
        return title if title else None

    def _validate_priority(self, priority: str | None) -> str | None:
        """Validiert und normalisiert eine Priorität. None ist erlaubt."""
        if priority is None:
            return None
        priority = priority.strip().capitalize()
        return priority if priority in PRIORITIES else None

    def _validate_category(self, category: str | None) -> str | None:
        """Validiert eine Kategorie gegen existierende Kategorien."""
        category = (category or "").strip() or None
        if category is not None and category not in set(self._repo.list_categories()):
            return None
        return category

    # ---------- Kategorien ----------

    def list_categories(self) -> List[str]:
        """Gibt alle Kategorien alphabetisch sortiert zurück."""
        cats = self._repo.list_categories()
        cats.sort(key=lambda x: x.lower())
        return cats

    def add_category(self, name: str) -> bool:
        """Fügt eine neue Kategorie hinzu."""
        name = (name or "").strip()
        if not name:
            return False
        return self._repo.add_category(name)

    def rename_category(self, old: str, new: str) -> bool:
        """Benennt eine Kategorie um."""
        old = (old or "").strip()
        new = (new or "").strip()
        if not old or not new:
            return False
        return self._repo.rename_category(old, new)

    def delete_category(self, name: str) -> bool:
        """Löscht eine Kategorie."""
        return self._repo.delete_category(name)

    # ---------- Tasks ----------

    def list_tasks(self) -> List[Task]:
        """Gibt alle Tasks zurück."""
        return self._repo.list_all()

    def add_task(
        self,
        title: str,
        due_date: date | None = None,
        category: str | None = None,
        priority: str | None = DEFAULT_PRIORITY,
    ) -> bool:
        """Fügt einen neuen Task hinzu. Gibt True zurück bei Erfolg."""
        validated_title = self._validate_title(title)
        if not validated_title:
            return False

        validated_category = self._validate_category(category)
        validated_priority = self._validate_priority(priority)

        self._repo.add(
            Task(
                id=self._repo.next_id(),
                title=validated_title,
                done=False,
                due_date=due_date,
                category=validated_category,
                priority=validated_priority,
            )
        )
        return True

    def delete_task(self, task_id: int) -> None:
        """Löscht einen Task."""
        self._repo.delete(task_id)

    def set_done(self, task_id: int, done: bool) -> None:
        """Setzt den Erledigt-Status eines Tasks."""
        self._repo.update(task_id, done=done)

    def rename_task(self, task_id: int, new_title: str) -> bool:
        """Benennt einen Task um. Gibt True zurück bei Erfolg."""
        validated_title = self._validate_title(new_title)
        if not validated_title:
            return False
        self._repo.update(task_id, title=validated_title)
        return True

    def set_due_date(self, task_id: int, due_date: date | None) -> None:
        """Setzt das Fälligkeitsdatum eines Tasks."""
        self._repo.update(task_id, due_date=due_date)

    def set_category(self, task_id: int, category: str | None) -> None:
        """Setzt die Kategorie eines Tasks."""
        validated_category = self._validate_category(category)
        self._repo.update(task_id, category=validated_category)

    def set_priority(self, task_id: int, priority: str | None) -> None:
        """Setzt die Priorität eines Tasks."""
        validated_priority = self._validate_priority(priority)
        self._repo.update(task_id, priority=validated_priority)

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        due_date: date | None = None,
        category: str | None = None,
        priority: str | None = None,
        update_due_date: bool = False,
        update_priority: bool = False,
    ) -> bool:
        """
        Aktualisiert einen Task mit mehreren Attributen auf einmal.
        Gibt True zurück bei Erfolg.
        """
        updates = {}

        if title is not None:
            validated_title = self._validate_title(title)
            if not validated_title:
                return False
            updates["title"] = validated_title

        if update_due_date:
            updates["due_date"] = due_date

        if category is not None:
            updates["category"] = self._validate_category(category)

        if update_priority:
            updates["priority"] = self._validate_priority(priority)

        if updates:
            self._repo.update(task_id, **updates)

        return True