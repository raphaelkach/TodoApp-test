from __future__ import annotations

from typing import List
from model.entities import Task
from model.service import TodoService


class TodoController:
    """Controller: Steuerungslogik / Use-Case-API für die View."""

    def __init__(self, service: TodoService):
        self.service = service

    def initialize(self) -> None:
        self.service.initialize()

    # Anlegen
    def add(self, title: str) -> None:
        self.service.add_task(title)

    # Anzeigen
    def list(self) -> List[Task]:
        return self.service.list_tasks()

    # Löschen
    def delete(self, task_id: int) -> None:
        self.service.delete_task(task_id)

    # Ändern (Status)
    def set_done(self, task_id: int, done: bool) -> None:
        self.service.set_done(task_id, done)

    # Ändern (Titel)
    def rename(self, task_id: int, new_title: str) -> None:
        self.service.rename_task(task_id, new_title)
