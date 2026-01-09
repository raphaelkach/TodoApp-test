"""
Controller für die Todo-App.
Koordiniert zwischen Model und View - OHNE UI-State-Management.
"""

from __future__ import annotations

from datetime import date
from typing import List

from model.entities import Task
from model.service import TodoService


class TodoController:
    """
    Controller zur Koordination zwischen Model und View.
    Verwaltet KEINEN UI-State - das macht die View selbst.
    """

    def __init__(self, service: TodoService) -> None:
        self._service = service

    # ---------- Initialisierung ----------

    def initialize(self) -> None:
        """Initialisiert den Service."""
        self._service.initialize()

    # ---------- Tasks (Daten) ----------

    def list_tasks(self) -> List[Task]:
        """Gibt alle Tasks zurück."""
        return self._service.list_tasks()

    def get_filtered_tasks(self, filter_value: str) -> List[Task]:
        """Gibt gefilterte Tasks zurück."""
        return self._service.get_filtered_tasks(filter_value)

    def get_task_counts(self) -> tuple[int, int, int]:
        """Gibt (alle, offen, erledigt) Anzahlen zurück."""
        return self._service.get_task_counts()

    # ---------- Tasks (Aktionen) ----------

    def add_task(
        self,
        title: str,
        due_date: date | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> bool:
        """Fügt einen neuen Task hinzu. Gibt True bei Erfolg zurück."""
        return self._service.add_task(title, due_date, category, priority)

    def update_task(
        self,
        task_id: int,
        title: str,
        due_date: date | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> bool:
        """Aktualisiert einen Task. Gibt True bei Erfolg zurück."""
        return self._service.update_task(
            task_id=task_id,
            title=title,
            due_date=due_date,
            category=category,
            priority=priority,
            update_due_date=True,
            update_priority=True,
        )

    def delete_task(self, task_id: int) -> None:
        """Löscht einen Task."""
        self._service.delete_task(task_id)

    def toggle_task_done(self, task_id: int, done: bool) -> None:
        """Setzt den Erledigt-Status eines Tasks."""
        self._service.set_done(task_id, done)

    # ---------- Kategorien (Daten) ----------

    def list_categories(self) -> List[str]:
        """Gibt alle Kategorien zurück."""
        return self._service.list_categories()

    def can_add_category(self) -> bool:
        """Prüft ob eine weitere Kategorie hinzugefügt werden kann."""
        return self._service.can_add_category()

    # ---------- Kategorien (Aktionen) ----------

    def add_category(self, name: str) -> bool:
        """Fügt eine neue Kategorie hinzu. Gibt True bei Erfolg zurück."""
        return self._service.add_category(name)

    def rename_category(self, old: str, new: str) -> bool:
        """Benennt eine Kategorie um. Gibt True bei Erfolg zurück."""
        return self._service.rename_category(old, new)

    def delete_category(self, name: str) -> bool:
        """Löscht eine Kategorie. Gibt True bei Erfolg zurück."""
        return self._service.delete_category(name)