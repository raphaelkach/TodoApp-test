"""
Unit Tests für die TODO-App.
"""

from datetime import date, timedelta
import pytest
from model.entities import Task
from model.repository import SessionStateTaskRepository
from model.service import TodoService
from controller.todo_controller import TodoController


@pytest.fixture
def service():
    """Service mit Repository."""
    state = {}
    repo = SessionStateTaskRepository(state)
    svc = TodoService(repo)
    svc.initialize()
    return svc


@pytest.fixture
def controller():
    """Controller mit Service."""
    state = {}
    repo = SessionStateTaskRepository(state)
    svc = TodoService(repo)
    ctrl = TodoController(svc)
    ctrl.initialize()
    return ctrl


class TestCore:
    """Kern-Funktionalität: Add, Delete, Edit, Done."""

    def test_add_and_delete(self, service):
        """Test: TODO-Item hinzufügen und entfernen."""
        # Add
        assert service.add_task("Task 1", priority="Hoch") is True
        assert len(service.list_tasks()) == 1
        assert service.list_tasks()[0].title == "Task 1"
        
        # Delete
        task_id = service.list_tasks()[0].id
        service.delete_task(task_id)
        assert len(service.list_tasks()) == 0

    def test_mark_done_and_undone(self, service):
        """Test: Als erledigt/nicht erledigt markieren."""
        service.add_task("Task")
        task_id = service.list_tasks()[0].id
        
        # Mark done
        service.set_done(task_id, True)
        assert service.list_tasks()[0].done is True
        
        # Mark undone
        service.set_done(task_id, False)
        assert service.list_tasks()[0].done is False

    def test_edit_task(self, service):
        """Test: Item bearbeiten."""
        service.add_task("Original")
        task_id = service.list_tasks()[0].id
        due = date.today() + timedelta(days=5)
        
        # Edit via update_task
        service.update_task(task_id, title="Updated", due_date=due, 
                          priority="Hoch", update_due_date=True, update_priority=True)
        
        task = service.list_tasks()[0]
        assert task.title == "Updated"
        assert task.due_date == due
        assert task.priority == "Hoch"

    def test_validation_errors(self, service):
        """Test: Fehlerfälle - leere Titel, ungültige Werte."""
        # Leere Titel
        assert service.add_task("") is False
        assert service.add_task("   ") is False
        
        # Ungültige Priorität
        service.add_task("Task", priority="Invalid")
        assert service.list_tasks()[0].priority is None


class TestCategories:
    """Kategorie-Verwaltung."""

    def test_category_lifecycle(self, service):
        """Test: Kategorien hinzufügen, umbenennen, löschen."""
        # Add
        assert service.add_category("Work") is True
        assert "Work" in service.list_categories()
        
        # Duplikat verhindern
        assert service.add_category("Work") is False
        
        # Rename
        assert service.rename_category("Work", "Job") is True
        assert "Job" in service.list_categories()
        assert "Work" not in service.list_categories()
        
        # Delete
        assert service.delete_category("Job") is True
        assert "Job" not in service.list_categories()
        
        # Max limit (5)
        for i in range(5):
            service.add_category(f"C{i}")
        assert service.add_category("C6") is False

    def test_category_with_tasks(self, service):
        """Test: Kategorie-Änderungen wirken sich auf Tasks aus."""
        # Kategorie erstellen und Task zuordnen
        service.add_category("Work")
        service.add_task("Task", category="Work")
        assert service.list_tasks()[0].category == "Work"
        
        # Kategorie umbenennen
        service.rename_category("Work", "Job")
        assert service.list_tasks()[0].category == "Job"
        
        # Kategorie löschen
        service.delete_category("Job")
        assert service.list_tasks()[0].category is None


class TestController:
    """Controller-Methoden (ohne UI-State)."""

    def test_controller_workflow(self, controller):
        """Test: Workflow via Controller-Methoden."""
        # Add
        assert controller.add_task("Task 1", priority="Hoch") is True
        assert len(controller.list_tasks()) == 1
        
        # Noch ein Task hinzufügen
        controller.add_task("Task 2")
        assert len(controller.list_tasks()) == 2
        
        # Done setzen
        task_id = controller.list_tasks()[1].id
        controller.toggle_task_done(task_id, True)
        assert controller.list_tasks()[1].done is True
        
        # Filter
        open_tasks = controller.get_filtered_tasks("Offen")
        done_tasks = controller.get_filtered_tasks("Erledigt")
        assert len(open_tasks) == 1
        assert len(done_tasks) == 1
        
        # Counts
        all_c, open_c, done_c = controller.get_task_counts()
        assert (all_c, open_c, done_c) == (2, 1, 1)

    def test_controller_categories(self, controller):
        """Test: Kategorie-Management via Controller."""
        # Hinzufügen
        assert controller.add_category("Work") is True
        assert "Work" in controller.list_categories()
        
        # Kann hinzufügen prüfen
        assert controller.can_add_category() is True
        
        # Umbenennen
        assert controller.rename_category("Work", "Job") is True
        assert "Job" in controller.list_categories()
        assert "Work" not in controller.list_categories()
        
        # Löschen
        assert controller.delete_category("Job") is True
        assert "Job" not in controller.list_categories()

    def test_controller_edit(self, controller):
        """Test: Task-Bearbeitung via Controller."""
        # Task erstellen
        controller.add_task("Original")
        task = controller.list_tasks()[0]
        
        # Update
        success = controller.update_task(
            task.id,
            title="Edited",
            priority="Hoch"
        )
        assert success is True
        
        updated = controller.list_tasks()[0]
        assert updated.title == "Edited"
        assert updated.priority == "Hoch"
        
        # Delete
        controller.delete_task(task.id)
        assert len(controller.list_tasks()) == 0


class TestEdgeCases:
    """Randbedingungen."""

    def test_edge_cases(self, service):
        """Test: Duplikate, Datum, Unicode."""
        # Duplikate erlaubt
        service.add_task("Dup")
        service.add_task("Dup")
        assert len([t for t in service.list_tasks() if t.title == "Dup"]) == 2
        
        # Datum (Past/Future)
        past = date.today() - timedelta(days=10)
        service.add_task("Past", due_date=past)
        assert service.list_tasks()[-1].due_date == past
        
        # Unicode
        service.add_task("✓ 你好 🎉")
        assert service.list_tasks()[-1].title == "✓ 你好 🎉"