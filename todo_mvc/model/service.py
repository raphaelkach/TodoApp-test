from __future__ import annotations

from typing import List
from model.entities import Task
from model.repository import SessionStateTaskRepository


class TodoService:
    """Service: Validierung + Geschäftslogik (UI-unabhängig)."""

    def __init__(self, repo: SessionStateTaskRepository):
        self.repo = repo

    def initialize(self) -> None:
        self.repo.ensure_initialized()

    # --- Anlegen ---
    def add_task(self, title: str) -> None:
        title = (title or "").strip()
        if not title:
            return
        task = Task(id=self.repo.next_id(), title=title, done=False)
        self.repo.add(task)

    # --- Anzeigen ---
    def list_tasks(self) -> List[Task]:
        return self.repo.list_all()

    # --- Löschen ---
    def delete_task(self, task_id: int) -> None:
        self.repo.delete(task_id)

    # --- Ändern: Status ---
    def set_done(self, task_id: int, done: bool) -> None:
        self.repo.set_done(task_id, done)

    # --- Ändern: Titel ---
    def rename_task(self, task_id: int, new_title: str) -> None:
        new_title = (new_title or "").strip()
        if not new_title:
            return
        self.repo.rename(task_id, new_title)
