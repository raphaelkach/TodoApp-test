from typing import List
from model.entities import Task
from model.service import TodoService


class TodoController:

    def __init__(self, service: TodoService):
        self.service = service

    def initialize(self) -> None:
        self.service.initialize()

    def add(self, title: str) -> None:
        self.service.add_task(title)

    def list(self) -> List[Task]:
        return self.service.list_tasks()

    def delete(self, task_id: int) -> None:
        self.service.delete_task(task_id)
