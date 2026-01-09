"""
Factory Pattern für die Todo-App.

Erstellt verschiedene Aufgabentypen flexibel, ohne dass der Client-Code
direkt die konkreten Klassen kennt.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

# Abstrakte Klasse Task mit describe()


class Task(ABC):
    """
    Abstrakte Basisklasse für alle Aufgabentypen.
    
    Definiert die gemeinsame Schnittstelle für alle Aufgaben.
    """

    @abstractmethod
    def describe(self) -> str:
        """
        Beschreibt die Aufgabe.
        """
        pass

# Konkrete Implementierungen



@dataclass
class TodoTask(Task):
    """
    Normale allgemeine Aufgabe.
    """

    title: str
    done: bool = False

    def describe(self) -> str:
        """Gibt Beschreibung im Format '[✓/○] ToDo: ...' zurück."""
        status = "✓" if self.done else "○"
        return f"[{status}] ToDo: {self.title}"


@dataclass
class ShoppingTask(Task):
    """
    Einkaufslisten-Aufgabe.
    
    Spezialisierte Aufgabe für Einkäufe.
    """

    item: str
    done: bool = False

    def describe(self) -> str:
        """Gibt Beschreibung im Format '[✓/○] Einkauf: ...' zurück."""
        status = "✓" if self.done else "○"
        return f"[{status}] Einkauf: {self.item}"


@dataclass
class WorkTask(Task):
    """
    Arbeitsaufgabe.
    
    Spezialisierte Aufgabe für berufliche Tätigkeiten.
    """

    title: str
    done: bool = False

    def describe(self) -> str:
        """Gibt Beschreibung im Format '[✓/○] Arbeit: ...' zurück."""
        status = "✓" if self.done else "○"
        return f"[{status}] Arbeit: {self.title}"

# TaskFactory mit create_task(type: str)


class TaskFactory:
    """
    Factory zum Erstellen verschiedener Aufgabentypen.
    """

    @staticmethod
    def create_task(task_type: str, title: str, **kwargs) -> Task:
        """
        Erstellt eine Aufgabe basierend auf dem Typ.
        
        Die Factory Method entscheidet anhand des Typs, welche
        konkrete Klasse instanziiert wird.
        """
        # Normalisiere Typ (lowercase, trim)
        task_type = task_type.lower().strip()
        done = kwargs.get("done", False)

        # Entscheidet welche Klasse instanziiert wird
        if task_type == "todo":
            return TodoTask(title=title, done=done)
        elif task_type == "shopping":
            return ShoppingTask(item=title, done=done)
        elif task_type == "work":
            return WorkTask(title=title, done=done)
        else:
            # Unbekannter Typ -> Fehler
            raise ValueError(f"Unbekannter Aufgabentyp: '{task_type}'")