"""
Externe API (Service) für das Adapter Pattern (MINIMAL VERSION).

Simuliert eine fiktive externe Aufgabenquelle mit inkompatiblem Datenformat.

Gemäß Folie 4:
"Erweitern Sie Ihre TODO-App um eine fiktive externe Aufgabenquelle 
(eigene mini-API), deren Datenformat nicht Ihrer internen Task-Klasse entspricht."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ExternalTodoItem:
    """
    Externes Datenformat - INKOMPATIBEL mit internem Task-Format.
    
    Unterschiede zum internen Format:
    - item_id: String statt int
    - name: statt title
    - is_completed: statt done
    - urgency: int (1-5) statt priority: str
    - label: statt category
    """

    item_id: str
    name: str
    is_completed: bool = False
    urgency: int = 3  # 1 (niedrig) bis 5 (hoch)
    label: str | None = None


class ExternalTodoService:
    """
    Simulierte externe API für Todo-Items.
    
    Dies ist der "Service" aus dem Adapter-Pattern:
    "Der Service ist eine nützliche Klasse mit einer inkompatiblen Schnittstelle."
    """

    def __init__(self):
        self._items: List[ExternalTodoItem] = []
        self._next_id = 1000

    def create_item(
        self,
        name: str,
        urgency: int = 3,
        label: str | None = None,
    ) -> ExternalTodoItem:
        """Erstellt ein neues externes Todo-Item."""
        item = ExternalTodoItem(
            item_id=f"EXT-{self._next_id}",
            name=name,
            is_completed=False,
            urgency=urgency,
            label=label,
        )
        self._items.append(item)
        self._next_id += 1
        return item

    def fetch_all(self) -> List[ExternalTodoItem]:
        """Ruft alle Items ab."""
        return list(self._items)