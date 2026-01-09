"""
Adapter Pattern für die Todo-App (MINIMAL VERSION).

Übersetzt externe Aufgabenobjekte in das interne Task-Format,
OHNE den bestehenden Code der TODO-App zu verändern.

Gemäß Folie 4:
"Der Adapter ist eine Klasse, die sowohl mit dem Client als auch 
mit dem Service zusammenarbeiten kann."
"""

from __future__ import annotations

from typing import List

from model.entities import Task
from adapter.external_api import ExternalTodoItem


# Mapping: Externe Urgency (1-5) -> Interne Priorität
URGENCY_TO_PRIORITY = {
    1: "Niedrig",
    2: "Niedrig",
    3: "Mittel",
    4: "Hoch",
    5: "Hoch",
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
            due_date=None,  # Externes Format hat kein Datum
            category=external.label,
            priority=self._convert_urgency(external.urgency),
        )

    def adapt_many(self, externals: List[ExternalTodoItem]) -> List[Task]:
        """Konvertiert mehrere externe Items."""
        return [self.adapt(ext) for ext in externals]