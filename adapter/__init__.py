"""
Adapter Pattern für die Todo-App.

Enthält:
- ExternalTodoService (externe API)
- ExternalTodoItem (externes Datenformat)
- TaskAdapter (Konvertierung extern -> intern)
- BidirectionalTaskAdapter (bidirektionale Konvertierung)
"""

from adapter.external_api import (
    ExternalTodoItem,
    ExternalTodoService,
)

from adapter.task_adapter import (
    TaskAdapter,
    BidirectionalTaskAdapter,
    URGENCY_TO_PRIORITY,
    PRIORITY_TO_URGENCY,
)

__all__ = [
    # External API
    "ExternalTodoItem",
    "ExternalTodoService",
    # Adapter
    "TaskAdapter",
    "BidirectionalTaskAdapter",
    "URGENCY_TO_PRIORITY",
    "PRIORITY_TO_URGENCY",
]
