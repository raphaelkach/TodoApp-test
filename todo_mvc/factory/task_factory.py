"""
Factory Pattern für die Todo-App.

Erstellt verschiedene Aufgabentypen flexibel, ohne dass der Client-Code
direkt die konkreten Klassen kennt.

Aufgabentypen:
- TodoTask – normale Aufgabe
- ShoppingTask – Einkaufsliste
- WorkTask – Arbeitsaufgabe
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


# ============================================================================
# 1. Abstrakte Klasse (Interface) Task mit describe()
# ============================================================================


class Task(ABC):
    """Abstrakte Basisklasse für alle Aufgabentypen."""

    @abstractmethod
    def describe(self) -> str:
        """Beschreibt die Aufgabe."""
        pass

    @abstractmethod
    def get_type(self) -> str:
        """Gibt den Aufgabentyp zurück."""
        pass


# ============================================================================
# 2. Konkrete Implementierungen
# ============================================================================


@dataclass
class TodoTask(Task):
    """Normale allgemeine Aufgabe."""

    title: str
    done: bool = False
    due_date: date | None = None

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        due = f" (bis {self.due_date.strftime('%d.%m.%Y')})" if self.due_date else ""
        return f"[{status}] ToDo: {self.title}{due}"

    def get_type(self) -> str:
        return "todo"


@dataclass
class ShoppingTask(Task):
    """Einkaufslisten-Aufgabe."""

    item: str
    quantity: int = 1
    done: bool = False
    store: str | None = None

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        store_info = f" @ {self.store}" if self.store else ""
        return f"[{status}] Einkauf: {self.quantity}x {self.item}{store_info}"

    def get_type(self) -> str:
        return "shopping"


@dataclass
class WorkTask(Task):
    """Arbeitsaufgabe mit Projekt und Deadline."""

    title: str
    project: str | None = None
    priority: str = "Mittel"
    done: bool = False
    deadline: date | None = None

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        proj = f" [{self.project}]" if self.project else ""
        prio = f" ({self.priority})" if self.priority else ""
        dl = f" bis {self.deadline.strftime('%d.%m.%Y')}" if self.deadline else ""
        return f"[{status}] Arbeit{proj}: {self.title}{prio}{dl}"

    def get_type(self) -> str:
        return "work"


# ============================================================================
# 3. TaskFactory mit create_task(type: str)
# ============================================================================


class TaskFactory:
    """
    Factory zum Erstellen verschiedener Aufgabentypen.
    
    Der Client-Code kennt nur die Factory, nicht die konkreten Klassen.
    
    Verwendung (wie im Foliensatz):
        factory = TaskFactory()
        task1 = factory.create_task("todo")
        task2 = factory.create_task("shopping")
        task3 = factory.create_task("work")
        
        task1.describe()  # Ausgabe: Dies ist eine allgemeine ToDo-Aufgabe.
    """

    @staticmethod
    def create_task(
        task_type: str,
        title: str = "Neue Aufgabe",
        **kwargs,
    ) -> Task:
        """
        Erstellt eine Aufgabe basierend auf dem Typ.
        
        Args:
            task_type: "todo", "shopping" oder "work"
            title: Titel/Name der Aufgabe
            **kwargs: Zusätzliche Parameter je nach Aufgabentyp
            
        Returns:
            Task-Objekt des entsprechenden Typs
            
        Raises:
            ValueError: Bei unbekanntem Aufgabentyp
        """
        task_type = task_type.lower().strip()

        if task_type == "todo":
            return TodoTask(
                title=title,
                done=kwargs.get("done", False),
                due_date=kwargs.get("due_date"),
            )

        elif task_type == "shopping":
            return ShoppingTask(
                item=title,
                quantity=kwargs.get("quantity", 1),
                done=kwargs.get("done", False),
                store=kwargs.get("store"),
            )

        elif task_type == "work":
            return WorkTask(
                title=title,
                project=kwargs.get("project"),
                priority=kwargs.get("priority", "Mittel"),
                done=kwargs.get("done", False),
                deadline=kwargs.get("deadline"),
            )

        else:
            raise ValueError(
                f"Unbekannter Aufgabentyp: '{task_type}'. "
                f"Erlaubt: 'todo', 'shopping', 'work'"
            )
