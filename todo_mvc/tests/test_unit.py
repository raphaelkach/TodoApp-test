"""
Unit-Tests für die Todo-App.

Ziel: ~80% Code-Coverage durch isolierte Tests der einzelnen Komponenten.
"""

from __future__ import annotations

from datetime import date
from typing import MutableMapping

import pytest

from model.entities import Task
from model.repository import SessionStateTaskRepository
from model.service import TodoService
from model.constants import DEFAULT_PRIORITY, MAX_CATEGORIES


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def state() -> MutableMapping:
    """Erstellt einen leeren Session State."""
    return {}


@pytest.fixture
def repo(state: MutableMapping) -> SessionStateTaskRepository:
    """Erstellt ein Repository mit leerem State."""
    return SessionStateTaskRepository(state)


@pytest.fixture
def service(repo: SessionStateTaskRepository) -> TodoService:
    """Erstellt einen Service mit leerem Repository."""
    return TodoService(repo)


# ============================================================================
# Entity Tests
# ============================================================================


class TestTask:
    """Tests für die Task-Entity."""

    def test_create_task_with_defaults(self):
        """Task mit Standardwerten erstellen."""
        task = Task(id=1, title="Test")
        
        assert task.id == 1
        assert task.title == "Test"
        assert task.done is False
        assert task.due_date is None
        assert task.category is None
        assert task.priority == DEFAULT_PRIORITY

    def test_create_task_with_all_fields(self):
        """Task mit allen Feldern erstellen."""
        due = date(2025, 12, 31)
        task = Task(
            id=1,
            title="Test",
            done=True,
            due_date=due,
            category="Arbeit",
            priority="Hoch",
        )
        
        assert task.done is True
        assert task.due_date == due
        assert task.category == "Arbeit"
        assert task.priority == "Hoch"

    def test_task_is_immutable(self):
        """Task ist unveränderlich (frozen)."""
        task = Task(id=1, title="Test")
        
        with pytest.raises(AttributeError):
            task.title = "Neuer Titel"


# ============================================================================
# Repository Tests
# ============================================================================


class TestRepository:
    """Tests für das Repository."""

    def test_ensure_initialized(self, repo: SessionStateTaskRepository, state: MutableMapping):
        """Repository initialisiert den State korrekt."""
        repo.ensure_initialized()
        
        assert "todos" in state
        assert "next_id" in state
        assert "categories" in state

    def test_add_and_list_task(self, repo: SessionStateTaskRepository):
        """Task hinzufügen und abrufen."""
        task = Task(id=repo.next_id(), title="Test Task")
        repo.add(task)
        
        tasks = repo.list_all()
        assert len(tasks) == 1
        assert tasks[0].title == "Test Task"

    def test_delete_task(self, repo: SessionStateTaskRepository):
        """Task löschen."""
        task = Task(id=repo.next_id(), title="Zu löschen")
        repo.add(task)
        
        repo.delete(task.id)
        
        assert len(repo.list_all()) == 0

    def test_update_task(self, repo: SessionStateTaskRepository):
        """Task aktualisieren."""
        task = Task(id=repo.next_id(), title="Original")
        repo.add(task)
        
        repo.update(task.id, title="Geändert", done=True)
        
        updated = repo.list_all()[0]
        assert updated.title == "Geändert"
        assert updated.done is True

    def test_next_id_increments(self, repo: SessionStateTaskRepository):
        """Jede ID ist eindeutig und inkrementiert."""
        id1 = repo.next_id()
        id2 = repo.next_id()
        id3 = repo.next_id()
        
        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

    # ---------- Kategorien ----------

    def test_add_category(self, repo: SessionStateTaskRepository):
        """Kategorie hinzufügen."""
        result = repo.add_category("Arbeit")
        
        assert result is True
        assert "Arbeit" in repo.list_categories()

    def test_add_duplicate_category_fails(self, repo: SessionStateTaskRepository):
        """Doppelte Kategorie wird abgelehnt."""
        repo.add_category("Arbeit")
        result = repo.add_category("Arbeit")
        
        assert result is False
        assert repo.list_categories().count("Arbeit") == 1

    def test_max_categories_limit(self, repo: SessionStateTaskRepository):
        """Maximal 5 Kategorien erlaubt."""
        for i in range(MAX_CATEGORIES):
            repo.add_category(f"Kat{i}")
        
        result = repo.add_category("Zu viel")
        
        assert result is False
        assert len(repo.list_categories()) == MAX_CATEGORIES

    def test_rename_category(self, repo: SessionStateTaskRepository):
        """Kategorie umbenennen."""
        repo.add_category("Alt")
        
        result = repo.rename_category("Alt", "Neu")
        
        assert result is True
        assert "Neu" in repo.list_categories()
        assert "Alt" not in repo.list_categories()

    def test_delete_category(self, repo: SessionStateTaskRepository):
        """Kategorie löschen."""
        repo.add_category("Temp")
        
        result = repo.delete_category("Temp")
        
        assert result is True
        assert "Temp" not in repo.list_categories()


# ============================================================================
# Service Tests
# ============================================================================


class TestService:
    """Tests für den Service."""

    def test_add_task_success(self, service: TodoService):
        """Task erfolgreich hinzufügen."""
        result = service.add_task("Neue Aufgabe")
        
        assert result is True
        assert len(service.list_tasks()) == 1

    def test_add_task_empty_title_fails(self, service: TodoService):
        """Leerer Titel wird abgelehnt."""
        result = service.add_task("")
        
        assert result is False
        assert len(service.list_tasks()) == 0

    def test_add_task_whitespace_title_fails(self, service: TodoService):
        """Nur-Whitespace-Titel wird abgelehnt."""
        result = service.add_task("   ")
        
        assert result is False
        assert len(service.list_tasks()) == 0

    def test_add_task_with_invalid_priority(self, service: TodoService):
        """Ungültige Priorität wird auf Standard gesetzt."""
        service.add_task("Test", priority="Ungültig")
        
        task = service.list_tasks()[0]
        assert task.priority == DEFAULT_PRIORITY

    def test_add_task_with_invalid_category(self, service: TodoService):
        """Ungültige Kategorie wird ignoriert."""
        service.add_task("Test", category="Existiert nicht")
        
        task = service.list_tasks()[0]
        assert task.category is None

    def test_set_done(self, service: TodoService):
        """Erledigt-Status setzen."""
        service.add_task("Test")
        task_id = service.list_tasks()[0].id
        
        service.set_done(task_id, True)
        
        assert service.list_tasks()[0].done is True

    def test_rename_task(self, service: TodoService):
        """Task umbenennen."""
        service.add_task("Alt")
        task_id = service.list_tasks()[0].id
        
        result = service.rename_task(task_id, "Neu")
        
        assert result is True
        assert service.list_tasks()[0].title == "Neu"

    def test_rename_task_empty_fails(self, service: TodoService):
        """Umbenennen mit leerem Titel schlägt fehl."""
        service.add_task("Original")
        task_id = service.list_tasks()[0].id
        
        result = service.rename_task(task_id, "")
        
        assert result is False
        assert service.list_tasks()[0].title == "Original"

    def test_categories_sorted_alphabetically(self, service: TodoService):
        """Kategorien werden alphabetisch sortiert."""
        service.add_category("Zebra")
        service.add_category("Apfel")
        service.add_category("Mango")
        
        cats = service.list_categories()
        
        assert cats == ["Apfel", "Mango", "Zebra"]


# ============================================================================
# Controller Tests (Basis-Funktionalität)
# ============================================================================


class TestController:
    """Tests für den Controller."""

    @pytest.fixture
    def controller(self, service: TodoService, state: MutableMapping):
        """Erstellt einen Controller."""
        from controller.todo_controller import TodoController
        return TodoController(service, state)

    def test_initialize(self, controller, state: MutableMapping):
        """Controller initialisiert UI-State."""
        controller.initialize()
        
        assert "editing_id" in state
        assert "new_title" in state
        assert "filter_raw" in state

    def test_add_task_from_state(self, controller, state: MutableMapping):
        """Task aus UI-State hinzufügen."""
        controller.initialize()
        state["new_title"] = "Test Aufgabe"
        
        controller.add_task()
        
        tasks = controller.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Test Aufgabe"
        assert state["new_title"] == ""  # Formular zurückgesetzt

    def test_add_task_empty_does_nothing(self, controller, state: MutableMapping):
        """Leerer Titel fügt keinen Task hinzu."""
        controller.initialize()
        state["new_title"] = ""
        
        controller.add_task()
        
        assert len(controller.list_tasks()) == 0

    def test_get_filtered_tasks_all(self, controller, state: MutableMapping):
        """Filter 'Alle' zeigt alle Tasks."""
        controller.initialize()
        state["new_title"] = "Task 1"
        controller.add_task()
        state["new_title"] = "Task 2"
        controller.add_task()
        
        # Einen als erledigt markieren
        task_id = controller.list_tasks()[0].id
        state[f"done_{task_id}"] = True
        controller.toggle_done(task_id)
        
        controller.set_filter("Alle")
        filtered = controller.get_filtered_tasks()
        
        assert len(filtered) == 2

    def test_get_filtered_tasks_open(self, controller, state: MutableMapping):
        """Filter 'Offen' zeigt nur offene Tasks."""
        controller.initialize()
        state["new_title"] = "Offen"
        controller.add_task()
        state["new_title"] = "Erledigt"
        controller.add_task()
        
        task_id = controller.list_tasks()[1].id
        state[f"done_{task_id}"] = True
        controller.toggle_done(task_id)
        
        controller.set_filter("Offen")
        filtered = controller.get_filtered_tasks()
        
        assert len(filtered) == 1
        assert filtered[0].title == "Offen"

    def test_get_task_counts(self, controller, state: MutableMapping):
        """Task-Zähler berechnen."""
        controller.initialize()
        state["new_title"] = "Task 1"
        controller.add_task()
        state["new_title"] = "Task 2"
        controller.add_task()
        
        task_id = controller.list_tasks()[0].id
        state[f"done_{task_id}"] = True
        controller.toggle_done(task_id)
        
        all_c, open_c, done_c = controller.get_task_counts()
        
        assert all_c == 2
        assert open_c == 1
        assert done_c == 1
