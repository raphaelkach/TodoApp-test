from __future__ import annotations

from datetime import date
from typing import List
from model.entities import Task
from model.repository import SessionStateTaskRepository


class TodoService:
    def __init__(self, repo: SessionStateTaskRepository):
        self.repo = repo

    def initialize(self) -> None:
        self.repo.ensure_initialized()

    def list_categories(self) -> List[str]:
        cats = self.repo.list_categories()
        cats.sort(key=lambda x: x.lower())
        return cats

    def add_category(self, name: str) -> None:
        name = (name or "").strip()
        if not name:
            return
        if len(self.repo.list_categories()) >= 5:
            return
        self.repo.add_category(name)

    def rename_category(self, old: str, new: str) -> None:
        old = (old or "").strip()
        new = (new or "").strip()
        if not old or not new:
            return
        self.repo.rename_category(old, new)

    def delete_category(self, name: str) -> None:
        self.repo.delete_category(name)

    def add_task(self, title: str, due_date: date | None = None, category: str | None = None) -> None:
        title = (title or "").strip()
        if not title:
            return

        category = (category or "").strip() or None
        if category is not None and category not in set(self.repo.list_categories()):
            category = None

        self.repo.add(
            Task(
                id=self.repo.next_id(),
                title=title,
                done=False,
                due_date=due_date,
                category=category,
            )
        )

    def list_tasks(self) -> List[Task]:
        return self.repo.list_all()

    def delete_task(self, task_id: int) -> None:
        self.repo.delete(task_id)

    def set_done(self, task_id: int, done: bool) -> None:
        self.repo.set_done(task_id, done)

    def rename_task(self, task_id: int, new_title: str) -> None:
        new_title = (new_title or "").strip()
        if not new_title:
            return
        self.repo.rename_task(task_id, new_title)

    def set_due_date(self, task_id: int, due_date: date | None) -> None:
        self.repo.set_due_date(task_id, due_date)

    def set_category(self, task_id: int, category: str | None) -> None:
        category = (category or "").strip() or None
        if category is not None and category not in set(self.repo.list_categories()):
            category = None
        self.repo.set_category(task_id, category)