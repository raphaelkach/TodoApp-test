"""
Externe API (Service) für das Adapter Pattern.

Simuliert eine fiktive externe Aufgabenquelle mit inkompatiblem Datenformat.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ExternalTodoItem:
    """
    Externes Datenformat - Inkompatibel mit internem Task-Format.
    """

    item_id: str
    name: str
    is_completed: bool = False
    urgency: int = 3  # 1 (niedrig) bis 5 (hoch)
    label: str | None = None


class ExternalTodoService:
    """
    Simulierte externe API für Todo-Items.
    """

    def __init__(self):
        """Initialisiert den Service mit leerer Item-Liste."""
        self._items: List[ExternalTodoItem] = []
        self._next_id = 1000

    def create_item(
        self,
        name: str,
        urgency: int = 3,
        label: str | None = None,
    ) -> ExternalTodoItem:
        """
        Erstellt ein neues externes Todo-Item.
        """
        item = ExternalTodoItem(
            item_id=f"EXT-{self._next_id}",  # Format: "EXT-1000"
            name=name,
            is_completed=False,
            urgency=urgency,
            label=label,
        )
        self._items.append(item)
        self._next_id += 1
        return item

    def fetch_all(self) -> List[ExternalTodoItem]:
        """
        Ruft alle Items ab.
        """
        return list(self._items)