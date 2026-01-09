"""
Adapter Pattern für die Todo-App (MINIMAL VERSION).

Enthält:
- ExternalTodoService (externe API)
- ExternalTodoItem (externes Datenformat)
- TaskAdapter (Konvertierung extern -> intern)
"""

from adapter.external_api import (
    ExternalTodoItem,
    ExternalTodoService,
)

from adapter.task_adapter import (
    TaskAdapter,
    URGENCY_TO_PRIORITY,
)

__all__ = [
    # External API
    "ExternalTodoItem",
    "ExternalTodoService",
    # Adapter
    "TaskAdapter",
    "URGENCY_TO_PRIORITY",
]