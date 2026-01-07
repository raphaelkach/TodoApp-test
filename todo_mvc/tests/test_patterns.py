"""
Tests für die Design Patterns der Todo-App.

Testet:
- Factory Pattern
- Abstract Factory Pattern
- Adapter Pattern
"""

import sys
from pathlib import Path

# Füge Parent-Verzeichnis zum Path hinzu für Imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datetime import date

# Factory Pattern Imports
from factory.task_factory import (
    Task,
    TodoTask,
    ShoppingTask,
    WorkTask,
    TaskFactory,
)

# Abstract Factory Pattern Imports
from factory.abstract_factory import (
    AbstractTask,
    SimpleTodoTask,
    SimpleShoppingTask,
    SimpleWorkTask,
    DetailedTodoTask,
    DetailedShoppingTask,
    DetailedWorkTask,
    AbstractTaskFactory,
    SimpleTaskFactory,
    DetailedTaskFactory,
)

# Adapter Pattern Imports
from adapter.external_api import ExternalTodoItem, ExternalTodoService
from adapter.task_adapter import TaskAdapter, BidirectionalTaskAdapter


# ============================================================================
# Factory Pattern Tests
# ============================================================================


class TestFactoryPattern:
    """Tests für das Factory Pattern."""

    def test_create_todo_task(self):
        """Factory erstellt TodoTask korrekt."""
        factory = TaskFactory()
        task = factory.create_task("todo", "Einkaufen gehen")

        assert isinstance(task, TodoTask)
        assert task.title == "Einkaufen gehen"
        assert task.get_type() == "todo"

    def test_create_shopping_task(self):
        """Factory erstellt ShoppingTask mit Extras."""
        factory = TaskFactory()
        task = factory.create_task(
            "shopping", "Milch", quantity=2, store="REWE"
        )

        assert isinstance(task, ShoppingTask)
        assert task.item == "Milch"
        assert task.quantity == 2
        assert task.store == "REWE"
        assert task.get_type() == "shopping"

    def test_create_work_task(self):
        """Factory erstellt WorkTask mit allen Parametern."""
        factory = TaskFactory()
        deadline = date(2025, 6, 15)
        task = factory.create_task(
            "work",
            "Präsentation erstellen",
            project="DHBW",
            priority="Hoch",
            deadline=deadline,
        )

        assert isinstance(task, WorkTask)
        assert task.title == "Präsentation erstellen"
        assert task.project == "DHBW"
        assert task.priority == "Hoch"
        assert task.deadline == deadline
        assert task.get_type() == "work"

    def test_create_task_case_insensitive(self):
        """Factory akzeptiert Typ-Strings case-insensitive."""
        factory = TaskFactory()

        task1 = factory.create_task("TODO", "Test1")
        task2 = factory.create_task("Todo", "Test2")
        task3 = factory.create_task("todo", "Test3")

        assert all(isinstance(t, TodoTask) for t in [task1, task2, task3])

    def test_create_task_unknown_type_raises(self):
        """Factory wirft ValueError bei unbekanntem Typ."""
        factory = TaskFactory()

        with pytest.raises(ValueError) as exc_info:
            factory.create_task("unknown", "Test")

        assert "Unbekannter Aufgabentyp" in str(exc_info.value)

    def test_describe_method(self):
        """describe() gibt formatierte Beschreibung zurück."""
        factory = TaskFactory()

        todo = factory.create_task("todo", "Folien wiederholen")
        shopping = factory.create_task("shopping", "Brot", quantity=2, store="Aldi")
        work = factory.create_task("work", "Meeting", project="Team", priority="Hoch")

        assert "ToDo" in todo.describe()
        assert "2x Brot" in shopping.describe()
        assert "[Team]" in work.describe()


# ============================================================================
# Abstract Factory Pattern Tests
# ============================================================================


class TestAbstractFactoryPattern:
    """Tests für das Abstract Factory Pattern."""

    def test_simple_factory_creates_simple_tasks(self):
        """SimpleTaskFactory erstellt einfache Aufgaben."""
        factory = SimpleTaskFactory()

        todo = factory.create_todo_task("Einfache Aufgabe")
        shopping = factory.create_shopping_task("Milch")
        work = factory.create_work_task("Meeting")

        assert isinstance(todo, SimpleTodoTask)
        assert isinstance(shopping, SimpleShoppingTask)
        assert isinstance(work, SimpleWorkTask)

    def test_detailed_factory_creates_detailed_tasks(self):
        """DetailedTaskFactory erstellt detaillierte Aufgaben."""
        factory = DetailedTaskFactory()

        todo = factory.create_todo_task(
            "Vorlesung",
            priority="Hoch",
            category="Uni",
            tags=["DHBW", "SE"],
        )
        shopping = factory.create_shopping_task(
            "Kaffee",
            quantity=500,
            unit="g",
            store="dm",
            price_estimate=8.99,
        )
        work = factory.create_work_task(
            "Sprint Planning",
            project="Todo-App",
            assignee="Max",
            estimated_hours=2.0,
        )

        assert isinstance(todo, DetailedTodoTask)
        assert isinstance(shopping, DetailedShoppingTask)
        assert isinstance(work, DetailedWorkTask)

        # Prüfe erweiterte Attribute
        assert todo.priority == "Hoch"
        assert todo.tags == ["DHBW", "SE"]
        assert shopping.price_estimate == 8.99
        assert work.estimated_hours == 2.0

    def test_simple_task_variant(self):
        """Simple-Tasks haben variant='simple' in Details."""
        factory = SimpleTaskFactory()
        todo = factory.create_todo_task("Test")

        details = todo.get_details()
        assert details["variant"] == "simple"

    def test_detailed_task_variant(self):
        """Detailed-Tasks haben variant='detailed' in Details."""
        factory = DetailedTaskFactory()
        todo = factory.create_todo_task("Test")

        details = todo.get_details()
        assert details["variant"] == "detailed"

    def test_factory_substitutability(self):
        """Factories sind austauschbar (Liskov Substitution)."""

        def create_tasks(factory: AbstractTaskFactory):
            return [
                factory.create_todo_task("Todo"),
                factory.create_shopping_task("Item"),
                factory.create_work_task("Work"),
            ]

        simple_tasks = create_tasks(SimpleTaskFactory())
        detailed_tasks = create_tasks(DetailedTaskFactory())

        # Beide Factory-Typen erstellen Tasks mit describe()
        for task in simple_tasks + detailed_tasks:
            assert isinstance(task, AbstractTask)
            assert callable(task.describe)
            assert isinstance(task.describe(), str)

    def test_abstract_task_describe(self):
        """Alle AbstractTask-Implementierungen haben describe()."""
        simple_factory = SimpleTaskFactory()
        detailed_factory = DetailedTaskFactory()

        simple_todo = simple_factory.create_todo_task("Einfach")
        detailed_todo = detailed_factory.create_todo_task("Detailliert", priority="Hoch")

        # Beide sollten beschreibende Strings zurückgeben
        assert "Einfach" in simple_todo.describe()
        assert "Detailliert" in detailed_todo.describe()


# ============================================================================
# Adapter Pattern Tests
# ============================================================================


class TestAdapterPattern:
    """Tests für das Adapter Pattern."""

    def test_external_service_creates_items(self):
        """ExternalTodoService erstellt Items im externen Format."""
        service = ExternalTodoService()
        item = service.create_item("Buy milk", urgency=4, label="Shopping")

        assert isinstance(item, ExternalTodoItem)
        assert item.name == "Buy milk"
        assert item.item_id.startswith("EXT-")
        assert item.urgency == 4
        assert item.label == "Shopping"

    def test_adapter_converts_id(self):
        """Adapter konvertiert String-ID zu Integer."""
        adapter = TaskAdapter(id_offset=10000)
        external = ExternalTodoItem(
            item_id="EXT-1000",
            name="Test",
        )

        task = adapter.adapt(external)

        # EXT-1000 -> 1000 + 10000 = 11000
        assert task.id == 11000

    def test_adapter_converts_fields(self):
        """Adapter konvertiert alle Felder korrekt."""
        adapter = TaskAdapter()
        external = ExternalTodoItem(
            item_id="EXT-100",
            name="Einkaufen",
            is_completed=True,
            due="2025-06-15T00:00:00",
            urgency=4,
            label="Haushalt",
        )

        task = adapter.adapt(external)

        assert task.title == "Einkaufen"
        assert task.done is True
        assert task.due_date == date(2025, 6, 15)
        assert task.priority == "Hoch"  # urgency 4 -> Hoch
        assert task.category == "Haushalt"

    def test_adapter_urgency_to_priority_mapping(self):
        """Adapter mappt Urgency korrekt zu Priority."""
        adapter = TaskAdapter()

        test_cases = [
            (1, "Niedrig"),
            (2, "Niedrig"),
            (3, "Mittel"),
            (4, "Hoch"),
            (5, "Hoch"),
        ]

        for urgency, expected_priority in test_cases:
            external = ExternalTodoItem(
                item_id=f"EXT-{urgency}",
                name="Test",
                urgency=urgency,
            )
            task = adapter.adapt(external)
            assert task.priority == expected_priority, f"Urgency {urgency} sollte {expected_priority} sein"

    def test_adapter_handles_null_due_date(self):
        """Adapter behandelt None-Werte korrekt."""
        adapter = TaskAdapter()
        external = ExternalTodoItem(
            item_id="EXT-1",
            name="Test",
            due=None,
            label=None,
        )

        task = adapter.adapt(external)

        assert task.due_date is None
        assert task.category is None

    def test_adapt_many(self):
        """Adapter konvertiert Liste von Items."""
        adapter = TaskAdapter()
        service = ExternalTodoService()

        service.create_item("Task 1")
        service.create_item("Task 2")
        service.create_item("Task 3")

        tasks = adapter.adapt_many(service.fetch_all())

        assert len(tasks) == 3
        assert all(hasattr(t, "title") for t in tasks)

    def test_bidirectional_adapter_to_external(self):
        """BidirectionalAdapter konvertiert zurück zu extern."""
        from model.entities import Task as InternalTask

        adapter = BidirectionalTaskAdapter()
        internal = InternalTask(
            id=1,
            title="Interner Task",
            done=False,
            due_date=date(2025, 7, 1),
            category="Arbeit",
            priority="Hoch",
        )

        external = adapter.to_external(internal)

        assert external.name == "Interner Task"
        assert external.is_completed is False
        assert "2025-07-01" in external.due
        assert external.urgency == 4  # Hoch -> 4
        assert external.label == "Arbeit"


# ============================================================================
# Integration Tests
# ============================================================================


class TestPatternIntegration:
    """Integrationstests für Pattern-Zusammenspiel."""

    def test_factory_to_adapter_workflow(self):
        """Factory erstellt Task, Adapter konvertiert zu extern und zurück."""
        # 1. Factory erstellt Task
        factory = TaskFactory()
        original = factory.create_task(
            "work",
            "Review PR",
            project="Backend",
            priority="Hoch",
            deadline=date(2025, 6, 20),
        )

        # 2. Bidirektionaler Adapter
        adapter = BidirectionalTaskAdapter()

        # Da Factory-Tasks andere Struktur haben, erstellen wir intern
        from model.entities import Task as InternalTask

        internal = InternalTask(
            id=1,
            title=original.title,
            done=original.done,
            due_date=original.deadline,
            category=original.project,
            priority=original.priority,
        )

        # 3. Konvertiere zu extern
        external = adapter.to_external(internal)
        assert external.name == "Review PR"
        assert external.urgency == 4  # Hoch

        # 4. Konvertiere zurück
        back = adapter.adapt(external)
        assert back.title == "Review PR"
        assert back.priority == "Hoch"

    def test_external_api_to_internal_workflow(self):
        """Kompletter Workflow: Externe API -> Adapter -> Interne Tasks."""
        # 1. Externe API liefert Items
        service = ExternalTodoService()
        service.create_item("Buy groceries", urgency=4, label="Shopping")
        service.create_item("Finish report", urgency=5, due="2025-06-15T00:00:00")
        service.create_item("Call mom", urgency=2)

        # 2. Adapter konvertiert alle
        adapter = TaskAdapter()
        tasks = adapter.adapt_many(service.fetch_all())

        # 3. Verifiziere
        assert len(tasks) == 3

        grocery_task = next(t for t in tasks if "groceries" in t.title)
        assert grocery_task.priority == "Hoch"
        assert grocery_task.category == "Shopping"

        report_task = next(t for t in tasks if "report" in t.title)
        assert report_task.priority == "Hoch"
        assert report_task.due_date == date(2025, 6, 15)


# ============================================================================
# Ausführung
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
