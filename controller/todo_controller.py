"""
Controller für die Todo-App.
Koordiniert zwischen Model und View.
"""

from __future__ import annotations

from datetime import date
from typing import List

from model.entities import Task
from model.service import TodoService


class TodoController:

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
        """
        Gibt gefilterte Tasks zurück.
        """
        return self._service.get_filtered_tasks(filter_value)

    def get_task_counts(self) -> tuple[int, int, int]:
        """
        Gibt Statistiken zurück.
        
        """
        return self._service.get_task_counts()

    # ---------- Tasks (Aktionen) ----------

    def add_task(
        self,
        title: str,
        due_date: date | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> bool:
        """
        Fügt einen neuen Task hinzu.
        """
        return self._service.add_task(title, due_date, category, priority)

    def update_task(
        self,
        task_id: int,
        title: str,
        due_date: date | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> bool:
        """
        Aktualisiert einen Task.
        """
        return self._service.update_task(
            task_id=task_id,
            title=title,
            due_date=due_date,
            category=category,
            priority=priority,
            update_due_date=True,  # Explizit updaten
            update_priority=True,   # Explizit updaten
        )

    def delete_task(self, task_id: int) -> None:
        """
        Löscht einen Task.
        """
        self._service.delete_task(task_id)

    def toggle_task_done(self, task_id: int, done: bool) -> None:
        """
        Setzt den Erledigt-Status eines Tasks.
        """
        self._service.set_done(task_id, done)

    # ---------- Kategorien (Daten) ----------

    def list_categories(self) -> List[str]:
        """Gibt alle Kategorien sortiert zurück."""
        return self._service.list_categories()

    def can_add_category(self) -> bool:
        """
        Prüft ob eine weitere Kategorie hinzugefügt werden kann.
        """
        return self._service.can_add_category()

    # ---------- Kategorien (Aktionen) ----------

    def add_category(self, name: str) -> bool:
        """
        Fügt eine neue Kategorie hinzu.
        """
        return self._service.add_category(name)

    def rename_category(self, old: str, new: str) -> bool:
        """
        Benennt eine Kategorie um.
        Aktualisiert automatisch alle Tasks mit dieser Kategorie.
        """
        return self._service.rename_category(old, new)

    def delete_category(self, name: str) -> bool:
        """
        Löscht eine Kategorie.
        Entfernt automatisch die Kategorie aus allen Tasks.
        """
        return self._service.delete_category(name)
