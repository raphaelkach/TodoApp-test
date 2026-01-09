"""Repository für den Datenzugriff auf Tasks und Kategorien."""

from __future__ import annotations

from datetime import date
from typing import List, MutableMapping

from model.entities import Task
from model.constants import (
    TASKS_KEY,
    NEXT_ID_KEY,
    CATEGORIES_KEY,
    MAX_CATEGORIES,
)


class SessionStateTaskRepository:
    """
    Repository zur Verwaltung von Tasks im Streamlit Session State.
    
    Das Repository ist die Datenzugriffsschicht:
    - Kapselt den Zugriff auf den Streamlit Session State
    - Keine Geschäftslogik, nur CRUD-Operationen
    - Gibt einfache Datenstrukturen zurück
    
    Session State Keys:
    - TASKS_KEY: Liste aller Tasks
    - NEXT_ID_KEY: Nächste verfügbare Task-ID
    - CATEGORIES_KEY: Liste aller Kategorien
    """

    def __init__(self, state: MutableMapping) -> None:
        """
        Initialisiert das Repository.
        """
        self._state = state

    def ensure_initialized(self) -> None:
        """
        Initialisiert den Session State falls nötig.
        
        Erstellt die benötigten Keys mit Default-Werten, falls diese noch nicht existieren.
        """
        if TASKS_KEY not in self._state:
            self._state[TASKS_KEY] = []
        if NEXT_ID_KEY not in self._state:
            self._state[NEXT_ID_KEY] = 1
        if CATEGORIES_KEY not in self._state:
            self._state[CATEGORIES_KEY] = []

    # ---------- Tasks ----------

    def list_all(self) -> List[Task]:
        """
        Gibt alle Tasks zurück.
        """
        self.ensure_initialized()
        return list(self._state[TASKS_KEY])

    def next_id(self) -> int:
        """
        Generiert die nächste eindeutige Task-ID.
        
        Implementiert einen einfachen Auto-Increment-Mechanismus.
        """
        self.ensure_initialized()
        nid = int(self._state[NEXT_ID_KEY])
        self._state[NEXT_ID_KEY] = nid + 1
        return nid

    def add(self, task: Task) -> None:
        """
        Fügt einen neuen Task hinzu.
        """
        self.ensure_initialized()
        self._state[TASKS_KEY].append(task)

    def delete(self, task_id: int) -> None:
        """
        Löscht einen Task anhand der ID.
    
        """
        self.ensure_initialized()
        # Filtert alle Tasks außer dem zu löschenden
        self._state[TASKS_KEY] = [
            t for t in self._state[TASKS_KEY] if t.id != task_id
        ]

    def update(self, task_id: int, **kwargs) -> None:
        """
        Aktualisiert einen Task mit den gegebenen Attributen.
        
        Erstellt ein neues Task-Objekt mit den aktualisierten Werten.
        Nicht angegebene Attribute behalten ihren alten Wert.
        """
        self.ensure_initialized()
        # Erstellt neue Task-Liste mit aktualisiertem Task
        self._state[TASKS_KEY] = [
            Task(
                id=t.id,
                title=kwargs.get("title", t.title),
                done=kwargs.get("done", t.done),
                due_date=kwargs.get("due_date", t.due_date),
                category=kwargs.get("category", t.category),
                priority=kwargs.get("priority", t.priority),
            )
            if t.id == task_id
            else t
            for t in self._state[TASKS_KEY]
        ]

    # ---------- Categories ----------

    def list_categories(self) -> List[str]:
        """
        Gibt alle Kategorien zurück.
        """
        self.ensure_initialized()
        return list(self._state[CATEGORIES_KEY])

    def add_category(self, name: str) -> bool:
        """
        Fügt eine neue Kategorie hinzu.
        """
        self.ensure_initialized()
        name = (name or "").strip()
        if not name:
            return False

        cats: list[str] = self._state[CATEGORIES_KEY]
        
        # Prüft Limit
        if len(cats) >= MAX_CATEGORIES:
            return False
        
        # Prüft Duplikat
        if name in cats:
            return False

        # Fügt hinzu
        cats.append(name)
        return True

    def rename_category(self, old: str, new: str) -> bool:
        """
        Benennt eine Kategorie um.
        """
        self.ensure_initialized()
        old = (old or "").strip()
        new = (new or "").strip()
        if not old or not new:
            return False

        cats: list[str] = self._state[CATEGORIES_KEY]
        
        # Prüft ob alte Kategorie existiert
        if old not in cats:
            return False
        
        # Prüft ob neuer Name bereits existiert (außer es ist der gleiche)
        if new in cats and new != old:
            return False

        # Benennt um
        self._state[CATEGORIES_KEY] = [new if c == old else c for c in cats]
        return True

    def delete_category(self, name: str) -> bool:
        """
        Löscht eine Kategorie.
        """
        self.ensure_initialized()
        name = (name or "").strip()
        if not name:
            return False

        cats: list[str] = self._state[CATEGORIES_KEY]
        
        # Prüft ob Kategorie existiert
        if name not in cats:
            return False

        # Löscht Kategorie
        self._state[CATEGORIES_KEY] = [c for c in cats if c != name]
        return True