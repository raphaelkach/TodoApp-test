from __future__ import annotations

from datetime import date
from typing import List, MutableMapping
from model.entities import Task

TASKS_KEY = "todos"
NEXT_ID_KEY = "next_id"
CATEGORIES_KEY = "categories"


class SessionStateTaskRepository:
    def __init__(self, state: MutableMapping):
        self._state = state

    def ensure_initialized(self) -> None:
        if TASKS_KEY not in self._state:
            self._state[TASKS_KEY] = []
        if NEXT_ID_KEY not in self._state:
            self._state[NEXT_ID_KEY] = 1
        if CATEGORIES_KEY not in self._state:
            self._state[CATEGORIES_KEY] = []

    # ---------- Tasks ----------
    def list_all(self) -> List[Task]:
        self.ensure_initialized()
        return list(self._state[TASKS_KEY])

    def next_id(self) -> int:
        self.ensure_initialized()
        nid = int(self._state[NEXT_ID_KEY])
        self._state[NEXT_ID_KEY] = nid + 1
        return nid

    def add(self, task: Task) -> None:
        self.ensure_initialized()
        self._state[TASKS_KEY].append(task)

    def delete(self, task_id: int) -> None:
        self.ensure_initialized()
        self._state[TASKS_KEY] = [
            t for t in self._state[TASKS_KEY] if t.id != task_id]

    def set_done(self, task_id: int, done: bool) -> None:
        self.ensure_initialized()
        self._state[TASKS_KEY] = [
            Task(id=t.id, title=t.title, done=done,
                 due_date=t.due_date, category=t.category)
            if t.id == task_id else t
            for t in self._state[TASKS_KEY]
        ]

    def rename_task(self, task_id: int, new_title: str) -> None:
        self.ensure_initialized()
        self._state[TASKS_KEY] = [
            Task(id=t.id, title=new_title, done=t.done,
                 due_date=t.due_date, category=t.category)
            if t.id == task_id else t
            for t in self._state[TASKS_KEY]
        ]

    def set_due_date(self, task_id: int, due_date: date | None) -> None:
        self.ensure_initialized()
        self._state[TASKS_KEY] = [
            Task(id=t.id, title=t.title, done=t.done,
                 due_date=due_date, category=t.category)
            if t.id == task_id else t
            for t in self._state[TASKS_KEY]
        ]

    def set_category(self, task_id: int, category: str | None) -> None:
        self.ensure_initialized()
        self._state[TASKS_KEY] = [
            Task(id=t.id, title=t.title, done=t.done,
                 due_date=t.due_date, category=category)
            if t.id == task_id else t
            for t in self._state[TASKS_KEY]
        ]

    def list_categories(self) -> List[str]:
        self.ensure_initialized()
        return list(self._state[CATEGORIES_KEY])

    def add_category(self, name: str) -> None:
        self.ensure_initialized()
        name = (name or "").strip()
        if not name:
            return

        cats: list[str] = self._state[CATEGORIES_KEY]
        if len(cats) >= 5:
            return
        if name in cats:
            return

        cats.append(name)

    def rename_category(self, old: str, new: str) -> None:
        self.ensure_initialized()
        old = (old or "").strip()
        new = (new or "").strip()
        if not old or not new:
            return

        cats: list[str] = self._state[CATEGORIES_KEY]
        if old not in cats:
            return
        if new in cats and new != old:
            return

        self._state[CATEGORIES_KEY] = [new if c == old else c for c in cats]

        self._state[TASKS_KEY] = [
            Task(id=t.id, title=t.title, done=t.done, due_date=t.due_date,
                 category=(new if t.category == old else t.category))
            for t in self._state[TASKS_KEY]
        ]

    def delete_category(self, name: str) -> None:
        self.ensure_initialized()
        name = (name or "").strip()
        if not name:
            return

        cats: list[str] = self._state[CATEGORIES_KEY]
        if name not in cats:
            return

        self._state[CATEGORIES_KEY] = [c for c in cats if c != name]

        self._state[TASKS_KEY] = [
            Task(
                id=t.id,
                title=t.title,
                done=t.done,
                due_date=t.due_date,
                category=(None if t.category == name else t.category),
            )
            for t in self._state[TASKS_KEY]
        ]
