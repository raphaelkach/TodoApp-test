"""
Abstract Factory Pattern für die Todo-App.

Erlaubt es, Familien verwandter Objekte zu erzeugen, ohne deren
konkrete Klassen angeben zu müssen.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# Abstrakte Produkte: AbstractTask mit describe()


class AbstractTask(ABC):
    """
    Abstraktes Produkt - Basis für alle Aufgaben.

    Definiert die gemeinsame Schnittstelle für alle Aufgaben-Varianten.
    """

    @abstractmethod
    def describe(self) -> str:
        """
        Beschreibt die Aufgabe.
        """
        pass

# Konkrete Produkte - Simple-Varianten (Familie 1)


@dataclass
class SimpleTodoTask(AbstractTask):
    """
    Einfache ToDo-Aufgabe.

    Minimalistische Variante mit nur Titel und Status.
    """

    title: str
    done: bool = False

    def describe(self) -> str:
        """Gibt einfache Beschreibung zurück."""
        status = "✓" if self.done else "○"
        return f"[{status}] {self.title}"


@dataclass
class SimpleShoppingTask(AbstractTask):
    """
    Einfache Einkaufsaufgabe.

    Minimalistische Variante mit nur Item und Status.
    """

    item: str
    done: bool = False

    def describe(self) -> str:
        """Gibt einfache Beschreibung zurück."""
        status = "✓" if self.done else "○"
        return f"[{status}] Kaufen: {self.item}"


@dataclass
class SimpleWorkTask(AbstractTask):
    """
    Einfache Arbeitsaufgabe.

    Minimalistische Variante mit nur Titel und Status.
    """

    title: str
    done: bool = False

    def describe(self) -> str:
        """Gibt einfache Beschreibung zurück."""
        status = "✓" if self.done else "○"
        return f"[{status}] Arbeit: {self.title}"

# Konkrete Produkte - Detailed-Varianten (Familie 2)


@dataclass
class DetailedTodoTask(AbstractTask):
    """
    Detaillierte ToDo-Aufgabe mit Metadaten.

    Erweiterte Variante mit Priorität und Kategorie.
    """

    title: str
    done: bool = False
    priority: str = "Mittel"
    category: str | None = None

    def describe(self) -> str:
        """
        Gibt detaillierte Beschreibung zurück.

        Zeigt nur relevante Metadaten (nicht Default-Werte).
        """
        status = "✓" if self.done else "○"
        details = []

        # Zeigt Priorität nur wenn nicht "Mittel"
        if self.priority != "Mittel":
            details.append(f"[{self.priority}]")

        # Zeigt Kategorie falls vorhanden
        if self.category:
            details.append(f"({self.category})")

        detail_str = " ".join(details)
        return f"[{status}] {self.title} {detail_str}".strip()


@dataclass
class DetailedShoppingTask(AbstractTask):
    """
    Detaillierte Einkaufsaufgabe mit Metadaten.

    Erweiterte Variante mit Menge und Geschäft.
    """

    item: str
    quantity: int = 1
    done: bool = False
    store: str | None = None

    def describe(self) -> str:
        """
        Gibt detaillierte Beschreibung zurück.

        Zeigt Menge und optional das Geschäft.
        """
        status = "✓" if self.done else "○"
        store_info = f" @ {self.store}" if self.store else ""
        return f"[{status}] {self.quantity}x {self.item}{store_info}"


@dataclass
class DetailedWorkTask(AbstractTask):
    """
    Detaillierte Arbeitsaufgabe mit Metadaten.

    Erweiterte Variante mit Projekt und Priorität.
    """

    title: str
    done: bool = False
    project: str | None = None
    priority: str = "Mittel"

    def describe(self) -> str:
        """
        Gibt detaillierte Beschreibung zurück.

        Zeigt Projekt und Priorität falls relevant.
        """
        status = "✓" if self.done else "○"
        proj = f"[{self.project}] " if self.project else ""
        prio = f" ({self.priority})" if self.priority != "Mittel" else ""
        return f"[{status}] {proj}{self.title}{prio}"

# Abstrakte Fabrik: AbstractTaskFactory


class AbstractTaskFactory(ABC):
    """
    Abstrakte Fabrik für Aufgaben.

    Definiert die Schnittstelle für die Erstellung von Aufgabenfamilien.
    Konkrete Fabriken entscheiden, welche Familie (Simple/Detailed) erstellt wird.
    """

    @abstractmethod
    def create_todo_task(self, title: str, **kwargs) -> AbstractTask:
        """
        Erstellt eine ToDo-Aufgabe.
        """
        pass

    @abstractmethod
    def create_shopping_task(self, item: str, **kwargs) -> AbstractTask:
        """
        Erstellt eine Einkaufsaufgabe.
        """
        pass

    @abstractmethod
    def create_work_task(self, title: str, **kwargs) -> AbstractTask:
        """
        Erstellt eine Arbeitsaufgabe.
        """
        pass


# Konkrete Fabriken


class SimpleTaskFactory(AbstractTaskFactory):
    """
    Fabrik für einfache Aufgaben.

    Erstellt Aufgaben der Simple-Familie mit minimalen Informationen.
    """

    def create_todo_task(self, title: str, **kwargs) -> SimpleTodoTask:
        """Erstellt SimpleTodoTask."""
        return SimpleTodoTask(
            title=title,
            done=kwargs.get("done", False),
        )

    def create_shopping_task(self, item: str, **kwargs) -> SimpleShoppingTask:
        """Erstellt SimpleShoppingTask."""
        return SimpleShoppingTask(
            item=item,
            done=kwargs.get("done", False),
        )

    def create_work_task(self, title: str, **kwargs) -> SimpleWorkTask:
        """Erstellt SimpleWorkTask."""
        return SimpleWorkTask(
            title=title,
            done=kwargs.get("done", False),
        )


class DetailedTaskFactory(AbstractTaskFactory):
    """
    Fabrik für detaillierte Aufgaben.
    """

    def create_todo_task(self, title: str, **kwargs) -> DetailedTodoTask:
        """
        Erstellt DetailedTodoTask.

        Unterstützt kwargs: done, priority, category
        """
        return DetailedTodoTask(
            title=title,
            done=kwargs.get("done", False),
            priority=kwargs.get("priority", "Mittel"),
            category=kwargs.get("category"),
        )

    def create_shopping_task(self, item: str, **kwargs) -> DetailedShoppingTask:
        """
        Erstellt DetailedShoppingTask.

        Unterstützt kwargs: quantity, done, store
        """
        return DetailedShoppingTask(
            item=item,
            quantity=kwargs.get("quantity", 1),
            done=kwargs.get("done", False),
            store=kwargs.get("store"),
        )

    def create_work_task(self, title: str, **kwargs) -> DetailedWorkTask:
        """
        Erstellt DetailedWorkTask.

        Unterstützt kwargs: done, project, priority
        """
        return DetailedWorkTask(
            title=title,
            done=kwargs.get("done", False),
            project=kwargs.get("project"),
            priority=kwargs.get("priority", "Mittel"),
        )
