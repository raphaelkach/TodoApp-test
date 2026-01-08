"""
Abstract Factory Pattern für die Todo-App.

Erlaubt es, Familien verwandter Objekte zu erzeugen, ohne deren
konkrete Klassen angeben zu müssen.

Produktfamilien:
- Simple: Einfache Aufgaben mit minimalen Informationen
- Detailed: Detaillierte Aufgaben mit allen Metadaten

Verwendung (wie im Foliensatz):
    factory = DetailedTaskFactory()  # oder SimpleTaskFactory()
    todo = factory.create_todo_task()
    shopping = factory.create_shopping_task()
    work = factory.create_work_task()
    
    todo.describe()  # Detaillierte ToDo-Aufgabe
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List


# ============================================================================
# 1. Abstrakte Produkte: AbstractTask mit describe()
# ============================================================================


class AbstractTask(ABC):
    """Abstraktes Produkt - Basis für alle Aufgaben."""

    @abstractmethod
    def describe(self) -> str:
        """Beschreibt die Aufgabe."""
        pass

    @abstractmethod
    def get_details(self) -> dict:
        """Gibt alle Details als Dictionary zurück."""
        pass


# ============================================================================
# 2. Konkrete Produkte - Simple-Varianten
# ============================================================================


@dataclass
class SimpleTodoTask(AbstractTask):
    """Einfache ToDo-Aufgabe mit nur Titel."""

    title: str
    done: bool = False

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        return f"[{status}] {self.title}"

    def get_details(self) -> dict:
        return {"type": "todo", "variant": "simple", "title": self.title, "done": self.done}


@dataclass
class SimpleShoppingTask(AbstractTask):
    """Einfache Einkaufsaufgabe mit nur Artikel."""

    item: str
    done: bool = False

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        return f"[{status}] Kaufen: {self.item}"

    def get_details(self) -> dict:
        return {"type": "shopping", "variant": "simple", "item": self.item, "done": self.done}


@dataclass
class SimpleWorkTask(AbstractTask):
    """Einfache Arbeitsaufgabe mit nur Titel."""

    title: str
    done: bool = False

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        return f"[{status}] Arbeit: {self.title}"

    def get_details(self) -> dict:
        return {"type": "work", "variant": "simple", "title": self.title, "done": self.done}


# ============================================================================
# 3. Konkrete Produkte - Detailed-Varianten
# ============================================================================


@dataclass
class DetailedTodoTask(AbstractTask):
    """Detaillierte ToDo-Aufgabe mit allen Metadaten."""

    title: str
    done: bool = False
    due_date: date | None = None
    category: str | None = None
    priority: str = "Mittel"
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        parts = [f"[{status}] {self.title}"]

        if self.priority != "Mittel":
            parts.append(f"[{self.priority}]")
        if self.category:
            parts.append(f"({self.category})")
        if self.due_date:
            parts.append(f"bis {self.due_date.strftime('%d.%m.%Y')}")
        if self.tags:
            parts.append(f"#{' #'.join(self.tags)}")

        return " ".join(parts)

    def get_details(self) -> dict:
        return {
            "type": "todo",
            "variant": "detailed",
            "title": self.title,
            "done": self.done,
            "due_date": self.due_date,
            "category": self.category,
            "priority": self.priority,
            "notes": self.notes,
            "created_at": self.created_at,
            "tags": self.tags,
        }


@dataclass
class DetailedShoppingTask(AbstractTask):
    """Detaillierte Einkaufsaufgabe mit allen Metadaten."""

    item: str
    quantity: int = 1
    unit: str = "Stück"
    done: bool = False
    store: str | None = None
    category: str | None = None
    price_estimate: float | None = None
    notes: str = ""

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        parts = [f"[{status}] {self.quantity} {self.unit} {self.item}"]

        if self.store:
            parts.append(f"@ {self.store}")
        if self.category:
            parts.append(f"({self.category})")
        if self.price_estimate:
            parts.append(f"~{self.price_estimate:.2f}€")

        return " ".join(parts)

    def get_details(self) -> dict:
        return {
            "type": "shopping",
            "variant": "detailed",
            "item": self.item,
            "quantity": self.quantity,
            "unit": self.unit,
            "done": self.done,
            "store": self.store,
            "category": self.category,
            "price_estimate": self.price_estimate,
            "notes": self.notes,
        }


@dataclass
class DetailedWorkTask(AbstractTask):
    """Detaillierte Arbeitsaufgabe mit allen Metadaten."""

    title: str
    done: bool = False
    project: str | None = None
    priority: str = "Mittel"
    deadline: date | None = None
    assignee: str | None = None
    estimated_hours: float | None = None
    description: str = ""
    subtasks: List[str] = field(default_factory=list)

    def describe(self) -> str:
        status = "✓" if self.done else "○"
        parts = [f"[{status}]"]

        if self.project:
            parts.append(f"[{self.project}]")

        parts.append(self.title)

        if self.priority != "Mittel":
            parts.append(f"({self.priority})")
        if self.deadline:
            parts.append(f"bis {self.deadline.strftime('%d.%m.%Y')}")
        if self.assignee:
            parts.append(f"→ {self.assignee}")
        if self.estimated_hours:
            parts.append(f"~{self.estimated_hours}h")

        return " ".join(parts)

    def get_details(self) -> dict:
        return {
            "type": "work",
            "variant": "detailed",
            "title": self.title,
            "done": self.done,
            "project": self.project,
            "priority": self.priority,
            "deadline": self.deadline,
            "assignee": self.assignee,
            "estimated_hours": self.estimated_hours,
            "description": self.description,
            "subtasks": self.subtasks,
        }


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
    
    Erstellt Aufgaben mit allen verfügbaren Metadaten.
    """

    def create_todo_task(self, title: str, **kwargs) -> DetailedTodoTask:
        return DetailedTodoTask(
            title=title,
            done=kwargs.get("done", False),
            due_date=kwargs.get("due_date"),
            category=kwargs.get("category"),
            priority=kwargs.get("priority", "Mittel"),
            notes=kwargs.get("notes", ""),
            tags=kwargs.get("tags", []),
        )

    def create_shopping_task(self, item: str, **kwargs) -> DetailedShoppingTask:
        return DetailedShoppingTask(
            item=item,
            quantity=kwargs.get("quantity", 1),
            unit=kwargs.get("unit", "Stück"),
            done=kwargs.get("done", False),
            store=kwargs.get("store"),
            category=kwargs.get("category"),
            price_estimate=kwargs.get("price_estimate"),
            notes=kwargs.get("notes", ""),
        )

    def create_work_task(self, title: str, **kwargs) -> DetailedWorkTask:
        return DetailedWorkTask(
            title=title,
            done=kwargs.get("done", False),
            project=kwargs.get("project"),
            priority=kwargs.get("priority", "Mittel"),
            deadline=kwargs.get("deadline"),
            assignee=kwargs.get("assignee"),
            estimated_hours=kwargs.get("estimated_hours"),
            description=kwargs.get("description", ""),
            subtasks=kwargs.get("subtasks", []),
        )
