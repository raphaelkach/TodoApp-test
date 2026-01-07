"""
Externe API (Service) für das Adapter Pattern.

Simuliert eine fiktive externe Aufgabenquelle mit einem Datenformat,
das NICHT dem internen Task-Format entspricht.

Gemäß Foliensatz Seite 21:
"Erweitern Sie Ihre TODO-App um eine fiktive externe Aufgabenquelle 
(eigene mini-API), deren Datenformat nicht Ihrer internen Task-Klasse entspricht."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class ExternalTodoItem:
    """
    Externes Datenformat - INKOMPATIBEL mit internem Task-Format.
    
    Unterschiede zum internen Format:
    - item_id: String statt int
    - name: statt title
    - is_completed: statt done
    - due: ISO-String statt date
    - urgency: 1-5 Skala statt "Niedrig"/"Mittel"/"Hoch"
    - label: statt category
    - created_timestamp: Unix-Timestamp
    """

    item_id: str
    name: str
    is_completed: bool = False
    due: str | None = None  # ISO-Format: "2025-06-15T00:00:00"
    urgency: int = 3  # 1 (niedrig) bis 5 (hoch)
    label: str | None = None
    created_timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary (für API-Simulation)."""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "is_completed": self.is_completed,
            "due": self.due,
            "urgency": self.urgency,
            "label": self.label,
            "created_timestamp": self.created_timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExternalTodoItem":
        """Erstellt aus Dictionary (für API-Simulation)."""
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            is_completed=data.get("is_completed", False),
            due=data.get("due"),
            urgency=data.get("urgency", 3),
            label=data.get("label"),
            created_timestamp=data.get("created_timestamp", datetime.now().timestamp()),
        )


class ExternalTodoService:
    """
    Simulierte externe API für Todo-Items.
    
    Dies ist der "Service" aus dem Adapter-Pattern (Foliensatz Seite 19):
    "Der Service ist eine nützliche Klasse mit einer inkompatiblen Schnittstelle."
    
    Verwendung:
        service = ExternalTodoService()
        item = service.create_item("Buy milk")
        items = service.fetch_all()
    """

    def __init__(self):
        self._items: List[ExternalTodoItem] = []
        self._next_id = 1000

    def _generate_id(self) -> str:
        """Generiert eine externe ID im Format 'EXT-XXXX'."""
        ext_id = f"EXT-{self._next_id}"
        self._next_id += 1
        return ext_id

    def create_item(
        self,
        name: str,
        due: str | None = None,
        urgency: int = 3,
        label: str | None = None,
    ) -> ExternalTodoItem:
        """Erstellt ein neues externes Todo-Item."""
        item = ExternalTodoItem(
            item_id=self._generate_id(),
            name=name,
            is_completed=False,
            due=due,
            urgency=urgency,
            label=label,
        )
        self._items.append(item)
        return item

    def fetch_all(self) -> List[ExternalTodoItem]:
        """Ruft alle Items ab."""
        return list(self._items)

    def fetch_by_id(self, item_id: str) -> ExternalTodoItem | None:
        """Ruft ein Item anhand der ID ab."""
        for item in self._items:
            if item.item_id == item_id:
                return item
        return None

    def complete_item(self, item_id: str) -> bool:
        """Markiert ein Item als erledigt."""
        item = self.fetch_by_id(item_id)
        if item:
            # Dataclass ist nicht frozen, also können wir es ändern
            item.is_completed = True
            return True
        return False

    def delete_item(self, item_id: str) -> bool:
        """Löscht ein Item."""
        for i, item in enumerate(self._items):
            if item.item_id == item_id:
                del self._items[i]
                return True
        return False
