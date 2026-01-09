"""
Abstract Factory Pattern für die Todo-App (MINIMAL VERSION).

Erlaubt es, Familien verwandter Objekte zu erzeugen, ohne deren
konkrete Klassen angeben zu müssen.

Gemäß Folie 3:
- AbstractTask mit describe()
- Simple: SimpleTodoTask, SimpleShoppingTask, SimpleWorkTask
- Detailed: DetailedTodoTask, DetailedShoppingTask, DetailedWorkTask
- AbstractTaskFactory, SimpleTaskFactory, DetailedTaskFactory
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ============================================================================
# 1. Abstrakte Produkte: AbstractTask mit describe()
# ============================================================================


class AbstractTask(ABC):
    """Abstraktes Produkt - Basis für alle Aufgaben."""

    @abstractmethod
    def describe(self) -> str:
        """Beschreibt die Aufgabe."""
        pass


# ============================================================================
# 2. Konkrete Produkte - Simple-Varianten
# ============================================================================


@dataclass
class SimpleTodoTask(AbstractTask):
    """Einfache ToDo-Aufgabe."""

    title: str
    done: bool = False

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        return f"[{status}] {self.title}"


@dataclass
class SimpleShoppingTask(AbstractTask):
    """Einfache Einkaufsaufgabe."""

    item: str
    done: bool = False

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        return f"[{status}] Kaufen: {self.item}"


@dataclass
class SimpleWorkTask(AbstractTask):
    """Einfache Arbeitsaufgabe."""

    title: str
    done: bool = False

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        return f"[{status}] Arbeit: {self.title}"


# ============================================================================
# 3. Konkrete Produkte - Detailed-Varianten
# ============================================================================


@dataclass
class DetailedTodoTask(AbstractTask):
    """Detaillierte ToDo-Aufgabe mit Metadaten."""

    title: str
    done: bool = False
    priority: str = "Mittel"
    category: str | None = None

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        details = []
        
        if self.priority != "Mittel":
            details.append(f"[{self.priority}]")
        if self.category:
            details.append(f"({self.category})")
        
        detail_str = " ".join(details)
        return f"[{status}] {self.title} {detail_str}".strip()


@dataclass
class DetailedShoppingTask(AbstractTask):
    """Detaillierte Einkaufsaufgabe mit Metadaten."""

    item: str
    quantity: int = 1
    done: bool = False
    store: str | None = None

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        store_info = f" @ {self.store}" if self.store else ""
        return f"[{status}] {self.quantity}x {self.item}{store_info}"


@dataclass
class DetailedWorkTask(AbstractTask):
    """Detaillierte Arbeitsaufgabe mit Metadaten."""

    title: str
    done: bool = False
    project: str | None = None
    priority: str = "Mittel"

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        proj = f"[{self.project}] " if self.project else ""
        prio = f" ({self.priority})" if self.priority != "Mittel" else ""
        return f"[{status}] {proj}{self.title}{prio}"


# ============================================================================
# 4. Abstrakte Fabrik: AbstractTaskFactory
# ============================================================================


class AbstractTaskFactory(ABC):
    """
    Abstrakte Fabrik für Aufgaben.
    
    Definiert die Schnittstelle für die Erstellung von Aufgabenfamilien.
    """

    @abstractmethod
    def create_todo_task(self, title: str, **kwargs) -> AbstractTask:
        """Erstellt eine ToDo-Aufgabe."""
        pass

    @abstractmethod
    def create_shopping_task(self, item: str, **kwargs) -> AbstractTask:
        """Erstellt eine Einkaufsaufgabe."""
        pass

    @abstractmethod
    def create_work_task(self, title: str, **kwargs) -> AbstractTask:
        """Erstellt eine Arbeitsaufgabe."""
        pass


# ============================================================================
# 5. Konkrete Fabriken
# ============================================================================


class SimpleTaskFactory(AbstractTaskFactory):
    """
    Fabrik für einfache Aufgaben.
    
    Erstellt Aufgaben mit minimalen Informationen.
    """

    def create_todo_task(self, title: str, **kwargs) -> SimpleTodoTask:
        return SimpleTodoTask(
            title=title,
            done=kwargs.get("done", False),
        )

    def create_shopping_task(self, item: str, **kwargs) -> SimpleShoppingTask:
        return SimpleShoppingTask(
            item=item,
            done=kwargs.get("done", False),
        )

    def create_work_task(self, title: str, **kwargs) -> SimpleWorkTask:
        return SimpleWorkTask(
            title=title,
            done=kwargs.get("done", False),
        )


class DetailedTaskFactory(AbstractTaskFactory):
    """
    Fabrik für detaillierte Aufgaben.
    
    Erstellt Aufgaben mit zusätzlichen Metadaten.
    """

    def create_todo_task(self, title: str, **kwargs) -> DetailedTodoTask:
        return DetailedTodoTask(
            title=title,
            done=kwargs.get("done", False),
            priority=kwargs.get("priority", "Mittel"),
            category=kwargs.get("category"),
        )

    def create_shopping_task(self, item: str, **kwargs) -> DetailedShoppingTask:
        return DetailedShoppingTask(
            item=item,
            quantity=kwargs.get("quantity", 1),
            done=kwargs.get("done", False),
            store=kwargs.get("store"),
        )

    def create_work_task(self, title: str, **kwargs) -> DetailedWorkTask:
        return DetailedWorkTask(
            title=title,
            done=kwargs.get("done", False),
            project=kwargs.get("project"),
            priority=kwargs.get("priority", "Mittel"),
        )