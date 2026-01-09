"""
Factory Patterns für die Todo-App (MINIMAL VERSION).

Enthält:
- Factory Pattern (TaskFactory)
- Abstract Factory Pattern (SimpleTaskFactory, DetailedTaskFactory)
"""

from factory.task_factory import (
    Task,
    TodoTask,
    ShoppingTask,
    WorkTask,
    TaskFactory,
)

from factory.abstract_factory import (
    AbstractTask,
    SimpleTodoTask,
    SimpleShoppingTask,
    SimpleWorkTask,
    DetailedTodoTask,
    DetailedShoppingTask,
    DetailedWorkTask,
    AbstractTaskFactory,
    SimpleTaskFactory,
    DetailedTaskFactory,
)

__all__ = [
    # Factory Pattern
    "Task",
    "TodoTask",
    "ShoppingTask",
    "WorkTask",
    "TaskFactory",
    # Abstract Factory Pattern
    "AbstractTask",
    "SimpleTodoTask",
    "SimpleShoppingTask",
    "SimpleWorkTask",
    "DetailedTodoTask",
    "DetailedShoppingTask",
    "DetailedWorkTask",
    "AbstractTaskFactory",
    "SimpleTaskFactory",
    "DetailedTaskFactory",
]