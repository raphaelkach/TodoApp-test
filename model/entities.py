"""Domänenobjekte für die Todo-App."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from model.constants import DEFAULT_PRIORITY


@dataclass(frozen=True)
class Task:
    """
    Repräsentiert eine Aufgabe in der Todo-Liste.
    
    Immutable Dataclass (frozen=True):
    - Verhindert versehentliche Modifikation
    - Erlaubt Verwendung als Dictionary-Key oder in Sets
    - Updates erfolgen durch Erstellen neuer Task-Objekte
    
    Attribute:
        id: Eindeutige ID der Aufgabe
        title: Beschreibung der Aufgabe (Pflichtfeld)
        done: Erledigt-Status (Default: False)
        due_date: Optional Fälligkeitsdatum
        category: Optional Kategorie-Zuordnung
        priority: Optional Priorität ("Niedrig", "Mittel", "Hoch")
    """

    id: int
    title: str
    done: bool = False
    due_date: date | None = None
    category: str | None = None
    priority: str | None = DEFAULT_PRIORITY