from typing import List
from .entities import Task
from .repository import SessionStateTaskRepository


class TodoService:

    def __init__(self, repo: SessionStateTaskRepository):
        self.repo = repo

    def initialize(self) -> None:
        self.repo.ensure_initialized()

    def add_task(self, title: str) -> None:
        title = (title or "").strip()
        if not title:
            return
        task = Task(id=self.repo.next_id(), title=title)
        self.repo.add(task)

    def list_tasks(self) -> List[Task]:
        return self.repo.list_all()

    def delete_task(self, task_id: int) -> None:
        self.repo.delete(task_id)
