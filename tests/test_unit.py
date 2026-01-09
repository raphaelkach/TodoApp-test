"""
Unit Tests für die TODO-App.

Test-Suite mit pytest für Model, Repository, Service und Controller.
Verwendet AAA-Pattern (Arrange-Act-Assert) und ist unabhängig lauffähig.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Dict

import pytest

from model.entities import Task
from model.repository import SessionStateTaskRepository
from model.service import TodoService
from controller.todo_controller import TodoController
from model.constants import (
    TASKS_KEY,
    NEXT_ID_KEY,
    CATEGORIES_KEY,
    PRIORITY_NONE_LABEL,
    CATEGORY_NONE_LABEL,
    FILTER_ALL,
    FILTER_OPEN,
    FILTER_DONE,
    UI_EDITING_ID,
    UI_NEW_TITLE,
    UI_FILTER_RAW,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_state() -> Dict:
    """Erstellt einen leeren Mock Session State."""
    return {}


@pytest.fixture
def repo(mock_state: Dict) -> SessionStateTaskRepository:
    """Erstellt ein Repository mit Mock State."""
    return SessionStateTaskRepository(mock_state)


@pytest.fixture
def service(repo: SessionStateTaskRepository) -> TodoService:
    """Erstellt einen Service mit Repository."""
    return TodoService(repo)


@pytest.fixture
def controller(service: TodoService, mock_state: Dict) -> TodoController:
    """Erstellt einen Controller mit Service und Mock State."""
    return TodoController(service, mock_state)


@pytest.fixture
def initialized_repo(repo: SessionStateTaskRepository) -> SessionStateTaskRepository:
    """Erstellt ein initialisiertes Repository."""
    repo.ensure_initialized()
    return repo


@pytest.fixture
def initialized_service(service: TodoService) -> TodoService:
    """Erstellt einen initialisierten Service."""
    service.initialize()
    return service


@pytest.fixture
def initialized_controller(controller: TodoController) -> TodoController:
    """Erstellt einen initialisierten Controller."""
    controller.initialize()
    return controller


# ============================================================================
# ENTITY TESTS
# ============================================================================

class TestTaskEntity:
    """Tests für die Task-Entity."""

    def test_task_creation_minimal(self):
        """Test: Task mit minimalen Attributen erstellen."""
        # Arrange & Act
        task = Task(id=1, title="Test Task")
        
        # Assert
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.done is False
        assert task.due_date is None
        assert task.category is None
        assert task.priority is None

    def test_task_creation_full(self):
        """Test: Task mit allen Attributen erstellen."""
        # Arrange
        due = date.today()
        
        # Act
        task = Task(
            id=1,
            title="Full Task",
            done=True,
            due_date=due,
            category="Work",
            priority="Hoch"
        )
        
        # Assert
        assert task.id == 1
        assert task.title == "Full Task"
        assert task.done is True
        assert task.due_date == due
        assert task.category == "Work"
        assert task.priority == "Hoch"

    def test_task_immutability(self):
        """Test: Task ist unveränderlich (frozen dataclass)."""
        # Arrange
        task = Task(id=1, title="Immutable")
        
        # Act & Assert
        with pytest.raises(AttributeError):
            task.title = "Changed"  # type: ignore


# ============================================================================
# REPOSITORY TESTS
# ============================================================================

class TestSessionStateTaskRepository:
    """Tests für das SessionStateTaskRepository."""

    # -------- Initialisierung --------

    def test_ensure_initialized_creates_keys(self, repo: SessionStateTaskRepository, mock_state: Dict):
        """Test: ensure_initialized erstellt alle benötigten Keys."""
        # Arrange
        assert TASKS_KEY not in mock_state
        
        # Act
        repo.ensure_initialized()
        
        # Assert
        assert TASKS_KEY in mock_state
        assert NEXT_ID_KEY in mock_state
        assert CATEGORIES_KEY in mock_state
        assert mock_state[TASKS_KEY] == []
        assert mock_state[NEXT_ID_KEY] == 1
        assert mock_state[CATEGORIES_KEY] == []

    def test_ensure_initialized_idempotent(self, initialized_repo: SessionStateTaskRepository, mock_state: Dict):
        """Test: ensure_initialized kann mehrfach aufgerufen werden."""
        # Arrange
        mock_state[NEXT_ID_KEY] = 5
        
        # Act
        initialized_repo.ensure_initialized()
        
        # Assert
        assert mock_state[NEXT_ID_KEY] == 5  # Wert bleibt erhalten

    # -------- Task Management --------

    def test_next_id_increments(self, initialized_repo: SessionStateTaskRepository, mock_state: Dict):
        """Test: next_id inkrementiert korrekt."""
        # Arrange & Act
        id1 = initialized_repo.next_id()
        id2 = initialized_repo.next_id()
        id3 = initialized_repo.next_id()
        
        # Assert
        assert id1 == 1
        assert id2 == 2
        assert id3 == 3
        assert mock_state[NEXT_ID_KEY] == 4

    def test_add_task(self, initialized_repo: SessionStateTaskRepository, mock_state: Dict):
        """Test: Task hinzufügen."""
        # Arrange
        task = Task(id=1, title="New Task")
        
        # Act
        initialized_repo.add(task)
        
        # Assert
        assert len(mock_state[TASKS_KEY]) == 1
        assert mock_state[TASKS_KEY][0] == task

    def test_list_all_tasks_empty(self, initialized_repo: SessionStateTaskRepository):
        """Test: Leere Task-Liste zurückgeben."""
        # Act
        tasks = initialized_repo.list_all()
        
        # Assert
        assert tasks == []

    def test_list_all_tasks_multiple(self, initialized_repo: SessionStateTaskRepository):
        """Test: Mehrere Tasks zurückgeben."""
        # Arrange
        task1 = Task(id=1, title="Task 1")
        task2 = Task(id=2, title="Task 2")
        initialized_repo.add(task1)
        initialized_repo.add(task2)
        
        # Act
        tasks = initialized_repo.list_all()
        
        # Assert
        assert len(tasks) == 2
        assert task1 in tasks
        assert task2 in tasks

    def test_delete_task(self, initialized_repo: SessionStateTaskRepository):
        """Test: Task löschen."""
        # Arrange
        task1 = Task(id=1, title="Keep")
        task2 = Task(id=2, title="Delete")
        initialized_repo.add(task1)
        initialized_repo.add(task2)
        
        # Act
        initialized_repo.delete(2)
        
        # Assert
        tasks = initialized_repo.list_all()
        assert len(tasks) == 1
        assert tasks[0].id == 1

    def test_delete_nonexistent_task(self, initialized_repo: SessionStateTaskRepository):
        """Test: Löschen eines nicht existierenden Tasks wirft keinen Fehler."""
        # Arrange
        task = Task(id=1, title="Task")
        initialized_repo.add(task)
        
        # Act
        initialized_repo.delete(999)  # Nicht existierende ID
        
        # Assert
        tasks = initialized_repo.list_all()
        assert len(tasks) == 1  # Task bleibt erhalten

    def test_update_task_title(self, initialized_repo: SessionStateTaskRepository):
        """Test: Task-Titel aktualisieren."""
        # Arrange
        task = Task(id=1, title="Old Title")
        initialized_repo.add(task)
        
        # Act
        initialized_repo.update(1, title="New Title")
        
        # Assert
        tasks = initialized_repo.list_all()
        assert tasks[0].title == "New Title"

    def test_update_task_done(self, initialized_repo: SessionStateTaskRepository):
        """Test: Task als erledigt markieren."""
        # Arrange
        task = Task(id=1, title="Task", done=False)
        initialized_repo.add(task)
        
        # Act
        initialized_repo.update(1, done=True)
        
        # Assert
        tasks = initialized_repo.list_all()
        assert tasks[0].done is True

    def test_update_task_multiple_fields(self, initialized_repo: SessionStateTaskRepository):
        """Test: Mehrere Task-Felder aktualisieren."""
        # Arrange
        task = Task(id=1, title="Task")
        initialized_repo.add(task)
        due = date.today()
        
        # Act
        initialized_repo.update(
            1,
            title="Updated",
            done=True,
            due_date=due,
            category="Work",
            priority="Hoch"
        )
        
        # Assert
        updated = initialized_repo.list_all()[0]
        assert updated.title == "Updated"
        assert updated.done is True
        assert updated.due_date == due
        assert updated.category == "Work"
        assert updated.priority == "Hoch"

    # -------- Category Management --------

    def test_list_categories_empty(self, initialized_repo: SessionStateTaskRepository):
        """Test: Leere Kategorienliste."""
        # Act
        categories = initialized_repo.list_categories()
        
        # Assert
        assert categories == []

    def test_add_category(self, initialized_repo: SessionStateTaskRepository, mock_state: Dict):
        """Test: Kategorie hinzufügen."""
        # Act
        result = initialized_repo.add_category("Work")
        
        # Assert
        assert result is True
        assert "Work" in mock_state[CATEGORIES_KEY]

    def test_add_duplicate_category(self, initialized_repo: SessionStateTaskRepository):
        """Test: Doppelte Kategorie nicht hinzufügen."""
        # Arrange
        initialized_repo.add_category("Work")
        
        # Act
        result = initialized_repo.add_category("Work")
        
        # Assert
        assert result is False
        assert initialized_repo.list_categories().count("Work") == 1

    def test_add_empty_category(self, initialized_repo: SessionStateTaskRepository):
        """Test: Leere Kategorie nicht hinzufügen."""
        # Act
        result = initialized_repo.add_category("")
        
        # Assert
        assert result is False
        assert len(initialized_repo.list_categories()) == 0

    def test_add_category_max_limit(self, initialized_repo: SessionStateTaskRepository):
        """Test: Maximale Anzahl Kategorien (5)."""
        # Arrange
        for i in range(5):
            initialized_repo.add_category(f"Cat{i}")
        
        # Act
        result = initialized_repo.add_category("Cat6")
        
        # Assert
        assert result is False
        assert len(initialized_repo.list_categories()) == 5

    def test_rename_category(self, initialized_repo: SessionStateTaskRepository):
        """Test: Kategorie umbenennen."""
        # Arrange
        initialized_repo.add_category("Old")
        
        # Act
        result = initialized_repo.rename_category("Old", "New")
        
        # Assert
        assert result is True
        categories = initialized_repo.list_categories()
        assert "New" in categories
        assert "Old" not in categories

    def test_rename_category_updates_tasks(self, initialized_repo: SessionStateTaskRepository):
        """Test: Umbenennen aktualisiert Tasks."""
        # Arrange
        initialized_repo.add_category("Old")
        task = Task(id=1, title="Task", category="Old")
        initialized_repo.add(task)
        
        # Act
        initialized_repo.rename_category("Old", "New")
        
        # Assert
        updated_task = initialized_repo.list_all()[0]
        assert updated_task.category == "New"

    def test_rename_to_existing_category(self, initialized_repo: SessionStateTaskRepository):
        """Test: Umbenennen zu existierender Kategorie schlägt fehl."""
        # Arrange
        initialized_repo.add_category("Cat1")
        initialized_repo.add_category("Cat2")
        
        # Act
        result = initialized_repo.rename_category("Cat1", "Cat2")
        
        # Assert
        assert result is False

    def test_delete_category(self, initialized_repo: SessionStateTaskRepository):
        """Test: Kategorie löschen."""
        # Arrange
        initialized_repo.add_category("Work")
        
        # Act
        result = initialized_repo.delete_category("Work")
        
        # Assert
        assert result is True
        assert "Work" not in initialized_repo.list_categories()

    def test_delete_category_removes_from_tasks(self, initialized_repo: SessionStateTaskRepository):
        """Test: Löschen entfernt Kategorie aus Tasks."""
        # Arrange
        initialized_repo.add_category("Work")
        task = Task(id=1, title="Task", category="Work")
        initialized_repo.add(task)
        
        # Act
        initialized_repo.delete_category("Work")
        
        # Assert
        updated_task = initialized_repo.list_all()[0]
        assert updated_task.category is None

    def test_delete_nonexistent_category(self, initialized_repo: SessionStateTaskRepository):
        """Test: Löschen nicht existierender Kategorie."""
        # Act
        result = initialized_repo.delete_category("Nonexistent")
        
        # Assert
        assert result is False


# ============================================================================
# SERVICE TESTS
# ============================================================================

class TestTodoService:
    """Tests für den TodoService."""

    # -------- Initialisierung --------

    def test_initialize(self, service: TodoService, mock_state: Dict):
        """Test: Service-Initialisierung."""
        # Act
        service.initialize()
        
        # Assert
        assert TASKS_KEY in mock_state
        assert NEXT_ID_KEY in mock_state
        assert CATEGORIES_KEY in mock_state

    # -------- Task Hinzufügen --------

    def test_add_task_minimal(self, initialized_service: TodoService):
        """Test: Task mit minimalen Daten hinzufügen."""
        # Act
        result = initialized_service.add_task("Test Task")
        
        # Assert
        assert result is True
        tasks = initialized_service.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Test Task"

    def test_add_task_full(self, initialized_service: TodoService):
        """Test: Task mit allen Daten hinzufügen."""
        # Arrange
        initialized_service.add_category("Work")
        due = date.today()
        
        # Act
        result = initialized_service.add_task(
            "Full Task",
            due_date=due,
            category="Work",
            priority="Hoch"
        )
        
        # Assert
        assert result is True
        task = initialized_service.list_tasks()[0]
        assert task.title == "Full Task"
        assert task.due_date == due
        assert task.category == "Work"
        assert task.priority == "Hoch"

    def test_add_task_empty_title(self, initialized_service: TodoService):
        """Test: Task mit leerem Titel nicht hinzufügen."""
        # Act
        result = initialized_service.add_task("")
        
        # Assert
        assert result is False
        assert len(initialized_service.list_tasks()) == 0

    def test_add_task_whitespace_title(self, initialized_service: TodoService):
        """Test: Task mit nur Leerzeichen nicht hinzufügen."""
        # Act
        result = initialized_service.add_task("   ")
        
        # Assert
        assert result is False
        assert len(initialized_service.list_tasks()) == 0

    def test_add_task_trims_title(self, initialized_service: TodoService):
        """Test: Titel wird getrimmt."""
        # Act
        initialized_service.add_task("  Task  ")
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.title == "Task"

    def test_add_task_invalid_category(self, initialized_service: TodoService):
        """Test: Ungültige Kategorie wird ignoriert."""
        # Act
        initialized_service.add_task("Task", category="NonExistent")
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.category is None

    def test_add_task_invalid_priority(self, initialized_service: TodoService):
        """Test: Ungültige Priorität wird ignoriert."""
        # Act
        initialized_service.add_task("Task", priority="Invalid")
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.priority is None

    # -------- Task Löschen --------

    def test_delete_task(self, initialized_service: TodoService):
        """Test: Task löschen."""
        # Arrange
        initialized_service.add_task("Task to Delete")
        task_id = initialized_service.list_tasks()[0].id
        
        # Act
        initialized_service.delete_task(task_id)
        
        # Assert
        assert len(initialized_service.list_tasks()) == 0

    # -------- Task Bearbeiten --------

    def test_set_done(self, initialized_service: TodoService):
        """Test: Task als erledigt markieren."""
        # Arrange
        initialized_service.add_task("Task")
        task_id = initialized_service.list_tasks()[0].id
        
        # Act
        initialized_service.set_done(task_id, True)
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.done is True

    def test_rename_task(self, initialized_service: TodoService):
        """Test: Task umbenennen."""
        # Arrange
        initialized_service.add_task("Old Name")
        task_id = initialized_service.list_tasks()[0].id
        
        # Act
        result = initialized_service.rename_task(task_id, "New Name")
        
        # Assert
        assert result is True
        task = initialized_service.list_tasks()[0]
        assert task.title == "New Name"

    def test_rename_task_empty(self, initialized_service: TodoService):
        """Test: Umbenennen mit leerem Titel schlägt fehl."""
        # Arrange
        initialized_service.add_task("Task")
        task_id = initialized_service.list_tasks()[0].id
        
        # Act
        result = initialized_service.rename_task(task_id, "")
        
        # Assert
        assert result is False

    def test_set_due_date(self, initialized_service: TodoService):
        """Test: Fälligkeitsdatum setzen."""
        # Arrange
        initialized_service.add_task("Task")
        task_id = initialized_service.list_tasks()[0].id
        due = date.today() + timedelta(days=7)
        
        # Act
        initialized_service.set_due_date(task_id, due)
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.due_date == due

    def test_set_category(self, initialized_service: TodoService):
        """Test: Kategorie setzen."""
        # Arrange
        initialized_service.add_category("Work")
        initialized_service.add_task("Task")
        task_id = initialized_service.list_tasks()[0].id
        
        # Act
        initialized_service.set_category(task_id, "Work")
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.category == "Work"

    def test_set_priority(self, initialized_service: TodoService):
        """Test: Priorität setzen."""
        # Arrange
        initialized_service.add_task("Task")
        task_id = initialized_service.list_tasks()[0].id
        
        # Act
        initialized_service.set_priority(task_id, "Hoch")
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.priority == "Hoch"

    def test_update_task_comprehensive(self, initialized_service: TodoService):
        """Test: Mehrere Felder gleichzeitig aktualisieren."""
        # Arrange
        initialized_service.add_category("Work")
        initialized_service.add_task("Old Task")
        task_id = initialized_service.list_tasks()[0].id
        due = date.today()
        
        # Act
        result = initialized_service.update_task(
            task_id,
            title="New Task",
            due_date=due,
            category="Work",
            priority="Mittel",
            update_due_date=True,
            update_priority=True
        )
        
        # Assert
        assert result is True
        task = initialized_service.list_tasks()[0]
        assert task.title == "New Task"
        assert task.due_date == due
        assert task.category == "Work"
        assert task.priority == "Mittel"

    # -------- Kategorie-Verwaltung --------

    def test_list_categories_sorted(self, initialized_service: TodoService):
        """Test: Kategorien alphabetisch sortiert."""
        # Arrange
        initialized_service.add_category("Zebra")
        initialized_service.add_category("Apple")
        initialized_service.add_category("Banana")
        
        # Act
        categories = initialized_service.list_categories()
        
        # Assert
        assert categories == ["Apple", "Banana", "Zebra"]

    def test_add_category(self, initialized_service: TodoService):
        """Test: Kategorie hinzufügen."""
        # Act
        result = initialized_service.add_category("Work")
        
        # Assert
        assert result is True
        assert "Work" in initialized_service.list_categories()

    def test_rename_category(self, initialized_service: TodoService):
        """Test: Kategorie umbenennen."""
        # Arrange
        initialized_service.add_category("Old")
        
        # Act
        result = initialized_service.rename_category("Old", "New")
        
        # Assert
        assert result is True
        categories = initialized_service.list_categories()
        assert "New" in categories
        assert "Old" not in categories

    def test_delete_category(self, initialized_service: TodoService):
        """Test: Kategorie löschen."""
        # Arrange
        initialized_service.add_category("Work")
        
        # Act
        result = initialized_service.delete_category("Work")
        
        # Assert
        assert result is True
        assert "Work" not in initialized_service.list_categories()

    # -------- Validierung --------

    def test_validate_priority_case_insensitive(self, initialized_service: TodoService):
        """Test: Priorität case-insensitive."""
        # Act
        initialized_service.add_task("Task", priority="hoch")
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.priority == "Hoch"


# ============================================================================
# CONTROLLER TESTS
# ============================================================================

class TestTodoController:
    """Tests für den TodoController."""

    # -------- Initialisierung --------

    def test_initialize(self, controller: TodoController, mock_state: Dict):
        """Test: Controller-Initialisierung."""
        # Act
        controller.initialize()
        
        # Assert
        assert UI_EDITING_ID in mock_state
        assert UI_NEW_TITLE in mock_state
        assert UI_FILTER_RAW in mock_state

    # -------- Task-Verwaltung --------

    def test_add_task(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Task über Controller hinzufügen."""
        # Arrange
        mock_state[UI_NEW_TITLE] = "Controller Task"
        
        # Act
        initialized_controller.add_task()
        
        # Assert
        tasks = initialized_controller.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Controller Task"
        assert mock_state[UI_NEW_TITLE] == ""  # Form zurückgesetzt

    def test_add_task_with_metadata(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Task mit Metadaten hinzufügen."""
        # Arrange
        initialized_controller.add_category()
        mock_state["cat_new_name"] = "Work"
        initialized_controller.add_category()
        
        due = date.today()
        mock_state[UI_NEW_TITLE] = "Task"
        mock_state["add_due_date"] = due
        mock_state["new_priority"] = "Hoch"
        mock_state["new_category"] = "Work"
        
        # Act
        initialized_controller.add_task()
        
        # Assert
        task = initialized_controller.list_tasks()[0]
        assert task.due_date == due
        assert task.priority == "Hoch"
        assert task.category == "Work"

    def test_delete_task(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Task löschen."""
        # Arrange
        mock_state[UI_NEW_TITLE] = "To Delete"
        initialized_controller.add_task()
        task_id = initialized_controller.list_tasks()[0].id
        
        # Act
        initialized_controller.delete_task(task_id)
        
        # Assert
        assert len(initialized_controller.list_tasks()) == 0

    def test_toggle_done(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Done-Status umschalten."""
        # Arrange
        mock_state[UI_NEW_TITLE] = "Task"
        initialized_controller.add_task()
        task_id = initialized_controller.list_tasks()[0].id
        mock_state[f"done_{task_id}"] = True
        
        # Act
        initialized_controller.toggle_done(task_id)
        
        # Assert
        task = initialized_controller.list_tasks()[0]
        assert task.done is True

    # -------- Task Bearbeiten --------

    def test_start_edit(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Bearbeitungsmodus starten."""
        # Arrange
        task_id = 1
        due = date.today()
        
        # Act
        initialized_controller.start_edit(
            task_id,
            "Title",
            due,
            "Work",
            "Hoch"
        )
        
        # Assert
        assert initialized_controller.is_editing(task_id)
        assert mock_state[f"title_{task_id}"] == "Title"
        assert mock_state[f"due_value_{task_id}"] == due
        assert mock_state[f"cat_sel_{task_id}"] == "Work"
        assert mock_state[f"prio_{task_id}"] == "Hoch"

    def test_save_edit(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Bearbeitung speichern."""
        # Arrange
        mock_state[UI_NEW_TITLE] = "Original"
        initialized_controller.add_task()
        task = initialized_controller.list_tasks()[0]
        
        initialized_controller.start_edit(
            task.id,
            task.title,
            task.due_date,
            task.category,
            task.priority
        )
        
        mock_state[f"title_{task.id}"] = "Edited"
        mock_state[f"prio_{task.id}"] = "Hoch"
        
        # Act
        initialized_controller.save_edit(task.id)
        
        # Assert
        updated = initialized_controller.list_tasks()[0]
        assert updated.title == "Edited"
        assert updated.priority == "Hoch"
        assert not initialized_controller.is_editing(task.id)

    def test_cancel_edit(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Bearbeitung abbrechen."""
        # Arrange
        task_id = 1
        initialized_controller.start_edit(task_id, "Title", None, None, None)
        mock_state[f"title_{task_id}"] = "Changed"
        
        # Act
        initialized_controller.cancel_edit(task_id, "Title", None, None, None)
        
        # Assert
        assert mock_state[f"title_{task_id}"] == "Title"
        assert not initialized_controller.is_editing(task_id)

    # -------- Filter --------

    def test_get_filter_default(self, initialized_controller: TodoController):
        """Test: Standard-Filter ist 'Alle'."""
        # Act
        filter_value = initialized_controller.get_filter()
        
        # Assert
        assert filter_value == FILTER_ALL

    def test_set_filter(self, initialized_controller: TodoController):
        """Test: Filter setzen."""
        # Act
        initialized_controller.set_filter(FILTER_OPEN)
        
        # Assert
        assert initialized_controller.get_filter() == FILTER_OPEN

    def test_get_filtered_tasks_all(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Alle Tasks filtern."""
        # Arrange
        mock_state[UI_NEW_TITLE] = "Task 1"
        initialized_controller.add_task()
        mock_state[UI_NEW_TITLE] = "Task 2"
        initialized_controller.add_task()
        
        # Act
        tasks = initialized_controller.get_filtered_tasks()
        
        # Assert
        assert len(tasks) == 2

    def test_get_filtered_tasks_open(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Nur offene Tasks filtern."""
        # Arrange
        mock_state[UI_NEW_TITLE] = "Open Task"
        initialized_controller.add_task()
        mock_state[UI_NEW_TITLE] = "Done Task"
        initialized_controller.add_task()
        
        done_task_id = initialized_controller.list_tasks()[1].id
        mock_state[f"done_{done_task_id}"] = True
        initialized_controller.toggle_done(done_task_id)
        
        initialized_controller.set_filter(FILTER_OPEN)
        
        # Act
        tasks = initialized_controller.get_filtered_tasks()
        
        # Assert
        assert len(tasks) == 1
        assert tasks[0].done is False

    def test_get_filtered_tasks_done(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Nur erledigte Tasks filtern."""
        # Arrange
        mock_state[UI_NEW_TITLE] = "Open Task"
        initialized_controller.add_task()
        mock_state[UI_NEW_TITLE] = "Done Task"
        initialized_controller.add_task()
        
        done_task_id = initialized_controller.list_tasks()[1].id
        mock_state[f"done_{done_task_id}"] = True
        initialized_controller.toggle_done(done_task_id)
        
        initialized_controller.set_filter(FILTER_DONE)
        
        # Act
        tasks = initialized_controller.get_filtered_tasks()
        
        # Assert
        assert len(tasks) == 1
        assert tasks[0].done is True

    def test_get_task_counts(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Task-Zähler abrufen."""
        # Arrange
        mock_state[UI_NEW_TITLE] = "Task 1"
        initialized_controller.add_task()
        mock_state[UI_NEW_TITLE] = "Task 2"
        initialized_controller.add_task()
        mock_state[UI_NEW_TITLE] = "Task 3"
        initialized_controller.add_task()
        
        task_id = initialized_controller.list_tasks()[0].id
        mock_state[f"done_{task_id}"] = True
        initialized_controller.toggle_done(task_id)
        
        # Act
        all_count, open_count, done_count = initialized_controller.get_task_counts()
        
        # Assert
        assert all_count == 3
        assert open_count == 2
        assert done_count == 1

    # -------- Kategorien --------

    def test_add_category(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Kategorie über Controller hinzufügen."""
        # Arrange
        mock_state["cat_new_name"] = "Work"
        
        # Act
        initialized_controller.add_category()
        
        # Assert
        assert "Work" in initialized_controller.list_categories()
        assert mock_state["cat_new_name"] == ""

    def test_can_add_category_limit(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Kategorie-Limit prüfen."""
        # Arrange
        for i in range(5):
            mock_state["cat_new_name"] = f"Cat{i}"
            initialized_controller.add_category()
        
        # Act
        can_add = initialized_controller.can_add_category()
        
        # Assert
        assert can_add is False

    def test_start_rename_category(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Kategorie-Umbenennung starten."""
        # Act
        initialized_controller.start_rename_category("Old")
        
        # Assert
        assert initialized_controller.get_rename_target() == "Old"
        assert mock_state["cat_rename_value"] == "Old"

    def test_save_rename_category(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Kategorie-Umbenennung speichern."""
        # Arrange
        mock_state["cat_new_name"] = "Old"
        initialized_controller.add_category()
        initialized_controller.start_rename_category("Old")
        mock_state["cat_rename_value"] = "New"
        
        # Act
        initialized_controller.save_rename_category("Old")
        
        # Assert
        assert "New" in initialized_controller.list_categories()
        assert "Old" not in initialized_controller.list_categories()
        assert initialized_controller.get_rename_target() is None

    def test_cancel_rename_category(self, initialized_controller: TodoController):
        """Test: Kategorie-Umbenennung abbrechen."""
        # Arrange
        initialized_controller.start_rename_category("Old")
        
        # Act
        initialized_controller.cancel_rename_category()
        
        # Assert
        assert initialized_controller.get_rename_target() is None

    def test_delete_category(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Kategorie über Controller löschen."""
        # Arrange
        mock_state["cat_new_name"] = "Work"
        initialized_controller.add_category()
        
        # Act
        initialized_controller.delete_category("Work")
        
        # Assert
        assert "Work" not in initialized_controller.list_categories()

    def test_delete_category_clears_ui_references(self, initialized_controller: TodoController, mock_state: Dict):
        """Test: Löschen bereinigt UI-Referenzen."""
        # Arrange
        mock_state["cat_new_name"] = "Work"
        initialized_controller.add_category()
        mock_state["new_category"] = "Work"
        mock_state["cat_sel_1"] = "Work"
        
        # Act
        initialized_controller.delete_category("Work")
        
        # Assert
        assert mock_state["new_category"] == CATEGORY_NONE_LABEL
        assert mock_state["cat_sel_1"] == CATEGORY_NONE_LABEL


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Tests für Randfälle und Fehlerbehandlung."""

    def test_add_task_with_future_due_date(self, initialized_service: TodoService):
        """Test: Task mit zukünftigem Datum."""
        # Arrange
        future = date.today() + timedelta(days=30)
        
        # Act
        initialized_service.add_task("Future Task", due_date=future)
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.due_date == future

    def test_add_task_with_past_due_date(self, initialized_service: TodoService):
        """Test: Task mit vergangenem Datum."""
        # Arrange
        past = date.today() - timedelta(days=30)
        
        # Act
        initialized_service.add_task("Past Task", due_date=past)
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.due_date == past

    def test_multiple_tasks_same_title(self, initialized_service: TodoService):
        """Test: Mehrere Tasks mit gleichem Titel erlaubt."""
        # Act
        initialized_service.add_task("Duplicate")
        initialized_service.add_task("Duplicate")
        
        # Assert
        tasks = initialized_service.list_tasks()
        assert len(tasks) == 2
        assert tasks[0].title == tasks[1].title
        assert tasks[0].id != tasks[1].id

    def test_category_name_with_special_characters(self, initialized_service: TodoService):
        """Test: Kategorie mit Sonderzeichen."""
        # Act
        result = initialized_service.add_category("Work & Home")
        
        # Assert
        assert result is True
        assert "Work & Home" in initialized_service.list_categories()

    def test_category_name_with_numbers(self, initialized_service: TodoService):
        """Test: Kategorie mit Zahlen."""
        # Act
        result = initialized_service.add_category("Project 2025")
        
        # Assert
        assert result is True
        assert "Project 2025" in initialized_service.list_categories()

    def test_priority_none_value(self, initialized_service: TodoService):
        """Test: Priorität None explizit setzen."""
        # Act
        initialized_service.add_task("Task", priority=None)
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.priority is None

    def test_update_nonexistent_task(self, initialized_repo: SessionStateTaskRepository):
        """Test: Update auf nicht existierenden Task."""
        # Act
        initialized_repo.update(999, title="Updated")
        
        # Assert - sollte keinen Fehler werfen
        assert len(initialized_repo.list_all()) == 0

    def test_very_long_title(self, initialized_service: TodoService):
        """Test: Sehr langer Titel."""
        # Arrange
        long_title = "A" * 1000
        
        # Act
        initialized_service.add_task(long_title)
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.title == long_title

    def test_unicode_in_title(self, initialized_service: TodoService):
        """Test: Unicode-Zeichen im Titel."""
        # Act
        initialized_service.add_task("Aufgabe ✓ 你好 🎉")
        
        # Assert
        task = initialized_service.list_tasks()[0]
        assert task.title == "Aufgabe ✓ 你好 🎉"

    def test_empty_task_list_operations(self, initialized_controller: TodoController):
        """Test: Operationen auf leerer Task-Liste."""
        # Act
        tasks = initialized_controller.get_filtered_tasks()
        all_c, open_c, done_c = initialized_controller.get_task_counts()
        
        # Assert
        assert tasks == []
        assert all_c == 0
        assert open_c == 0
        assert done_c == 0