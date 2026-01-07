"""
Adapter Pattern für die Todo-App.

Übersetzt externe Aufgabenobjekte in das interne Task-Format,
OHNE den bestehenden Code der TODO-App zu verändern.

Gemäß Foliensatz Seite 19:
"Der Adapter ist eine Klasse, die sowohl mit dem Client als auch 
mit dem Service zusammenarbeiten kann."

Verwendung (wie im Foliensatz Seite 23):
    external = ExternalTodoService().create_item("Buy milk")
    task = TaskAdapter().adapt(external)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List

from model.entities import Task
from adapter.external_api import ExternalTodoItem, ExternalTodoService


# Mapping: Externe Urgency (1-5) -> Interne Priorität
URGENCY_TO_PRIORITY = {
    1: "Niedrig",
    2: "Niedrig",
    3: "Mittel",
    4: "Hoch",
    5: "Hoch",
}

# Reverse Mapping: Interne Priorität -> Externe Urgency
PRIORITY_TO_URGENCY = {
    "Niedrig": 2,
    "Mittel": 3,
    "Hoch": 4,
}


class TaskAdapter:
    """
    Adapter: Konvertiert ExternalTodoItem -> internes Task-Format.
    
    Dies implementiert das Adapter-Pattern (Strukturmuster):
    - Client: Die Todo-App (verwendet Task-Objekte)
    - Service: ExternalTodoService (liefert ExternalTodoItem)
    - Adapter: TaskAdapter (übersetzt zwischen beiden)
    
    Konvertierungen:
    - item_id (String "EXT-1000") -> id (int, z.B. 11000)
    - name -> title
    - is_completed -> done
    - due (ISO-String) -> due_date (date)
    - urgency (1-5) -> priority ("Niedrig"/"Mittel"/"Hoch")
    - label -> category
    """

    def __init__(self, id_offset: int = 10000):
        """
        Args:
            id_offset: Offset für ID-Konvertierung (verhindert Kollisionen)
        """
        self._id_offset = id_offset

    def _convert_id(self, external_id: str) -> int:
        """
        Konvertiert externe ID zu interner ID.
        
        "EXT-1000" -> 11000 (mit Offset 10000)
        """
        try:
            num_part = external_id.split("-")[-1]
            return int(num_part) + self._id_offset
        except (ValueError, IndexError):
            # Fallback: Hash der ID
            return abs(hash(external_id)) % 100000 + self._id_offset

    def _convert_due_date(self, due: str | None) -> date | None:
        """Konvertiert ISO-String zu date."""
        if not due:
            return None
        try:
            return datetime.fromisoformat(due).date()
        except ValueError:
            return None

    def _convert_urgency(self, urgency: int) -> str:
        """Konvertiert Urgency (1-5) zu Priority-String."""
        return URGENCY_TO_PRIORITY.get(urgency, "Mittel")

    def adapt(self, external: ExternalTodoItem) -> Task:
        """
        Konvertiert ein externes Item zum internen Task-Format.
        
        Args:
            external: Externes Todo-Item
            
        Returns:
            Internes Task-Objekt
        """
        return Task(
            id=self._convert_id(external.item_id),
            title=external.name,
            done=external.is_completed,
            due_date=self._convert_due_date(external.due),
            category=external.label,
            priority=self._convert_urgency(external.urgency),
        )

    def adapt_many(self, externals: List[ExternalTodoItem]) -> List[Task]:
        """Konvertiert mehrere externe Items."""
        return [self.adapt(ext) for ext in externals]


class BidirectionalTaskAdapter(TaskAdapter):
    """
    Erweiterter Adapter für bidirektionale Konvertierung.
    
    Ermöglicht auch die Rückkonvertierung:
    - Task -> ExternalTodoItem
    """

    def to_external(self, task: Task, external_id: str | None = None) -> ExternalTodoItem:
        """
        Konvertiert ein internes Task zum externen Format.
        
        Args:
            task: Internes Task-Objekt
            external_id: Optionale externe ID (sonst generiert)
            
        Returns:
            Externes Todo-Item
        """
        if external_id is None:
            external_id = f"EXT-{task.id}"

        due_str = None
        if task.due_date:
            due_str = datetime.combine(task.due_date, datetime.min.time()).isoformat()

        return ExternalTodoItem(
            item_id=external_id,
            name=task.title,
            is_completed=task.done,
            due=due_str,
            urgency=PRIORITY_TO_URGENCY.get(task.priority, 3),
            label=task.category,
        )
