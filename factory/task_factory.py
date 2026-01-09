"""
Factory Pattern für die Todo-App (MINIMAL VERSION).

Erstellt verschiedene Aufgabentypen flexibel, ohne dass der Client-Code
direkt die konkreten Klassen kennt.

Gemäß Folie 2:
- Abstrakte Klasse Task mit describe()
- TodoTask, ShoppingTask, WorkTask
- TaskFactory mit create_task(type: str)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ============================================================================
# 1. Abstrakte Klasse Task mit describe()
# ============================================================================


class Task(ABC):
    """Abstrakte Basisklasse für alle Aufgabentypen."""

    @abstractmethod
    def describe(self) -> str:
        """Beschreibt die Aufgabe."""
        pass


# ============================================================================
# 2. Konkrete Implementierungen
# ============================================================================


@dataclass
class TodoTask(Task):
    """Normale allgemeine Aufgabe."""

    title: str
    done: bool = False

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        return f"[{status}] ToDo: {self.title}"


@dataclass
class ShoppingTask(Task):
    """Einkaufslisten-Aufgabe."""

    item: str
    done: bool = False

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        return f"[{status}] Einkauf: {self.item}"


@dataclass
class WorkTask(Task):
    """Arbeitsaufgabe."""

    title: str
    done: bool = False

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        return f"[{status}] Arbeit: {self.title}"


# ============================================================================
# 3. TaskFactory mit create_task(type: str)
# ============================================================================


class TaskFactory:
    """
    Factory zum Erstellen verschiedener Aufgabentypen.
    
    Der Client-Code kennt nur die Factory, nicht die konkreten Klassen.
    
    Verwendung (wie im Foliensatz):
        factory = TaskFactory()
        task1 = factory.create_task("todo", title="Folien wiederholen")
        task2 = factory.create_task("shopping", title="Milch")
        task3 = factory.create_task("work", title="Meeting")
        
        task1.describe()  # [○] ToDo: Folien wiederholen
    """

    @staticmethod
    def create_task(task_type: str, title: str, **kwargs) -> Task:
        """
        Erstellt eine Aufgabe basierend auf dem Typ.
        
        Args:
            task_type: "todo", "shopping" oder "work"
            title: Titel/Name der Aufgabe
            **kwargs: done (optional)
            
        Returns:
            Task-Objekt des entsprechenden Typs
            
        Raises:
            ValueError: Bei unbekanntem Aufgabentyp
        """
        task_type = task_type.lower().strip()
        done = kwargs.get("done", False)

        if task_type == "todo":
            return TodoTask(title=title, done=done)
        elif task_type == "shopping":
            return ShoppingTask(item=title, done=done)
        elif task_type == "work":
            return WorkTask(title=title, done=done)
        else:
            raise ValueError(f"Unbekannter Aufgabentyp: '{task_type}'")