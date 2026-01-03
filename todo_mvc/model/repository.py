from __future__ import annotations

from typing import List, MutableMapping
from model.entities import Task

TASKS_KEY = "todos"
NEXT_ID_KEY = "next_id"


class SessionStateTaskRepository:
    def __init__(self, state: MutableMapping):
        self._state = state

    def ensure_initialized(self) -> None:
        if TASKS_KEY not in self._state:
            self._state[TASKS_KEY] = []
        if NEXT_ID_KEY not in self._state:
            self._state[NEXT_ID_KEY] = 1

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
        self._state[TASKS_KEY] = [t for t in self._state[TASKS_KEY] if t.id != task_id]

    def set_done(self, task_id: int, done: bool) -> None:
        self.ensure_initialized()
        self._state[TASKS_KEY] = [
            Task(id=t.id, title=t.title, done=done) if t.id == task_id else t
            for t in self._state[TASKS_KEY]
        ]

    def rename(self, task_id: int, new_title: str) -> None:
        self.ensure_initialized()
        self._state[TASKS_KEY] = [
            Task(id=t.id, title=new_title, done=t.done) if t.id == task_id else t
            for t in self._state[TASKS_KEY]
        ]