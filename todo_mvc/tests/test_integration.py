"""
Integrationstests für die Todo-App.

Ziel: 3-4 Tests die das Zusammenspiel mehrerer Komponenten prüfen.
"""

from __future__ import annotations

from datetime import date
from typing import MutableMapping

import pytest

from model.repository import SessionStateTaskRepository
from model.service import TodoService
from controller.todo_controller import TodoController


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def state() -> MutableMapping:
    """Erstellt einen leeren Session State."""
    return {}


@pytest.fixture
def system(state: MutableMapping) -> tuple[TodoController, MutableMapping]:
    """Erstellt das komplette MVC-System."""
    repo = SessionStateTaskRepository(state)
    service = TodoService(repo)
    controller = TodoController(service, state)
    controller.initialize()
    return controller, state


# ============================================================================
# Integrationstests
# ============================================================================


class TestIntegration:
    """Integrationstests für das Zusammenspiel der Komponenten."""

    def test_task_lifecycle_create_complete_delete(self, system):
        """
        Test 1: Vollständiger Task-Lebenszyklus.
        
        Prüft: Repository ↔ Service ↔ Controller
        """
        controller, state = system
        
        # 1. Task erstellen
        state["new_title"] = "Integration Test Task"
        state["new_priority"] = "Hoch"
        controller.add_task()
        
        tasks = controller.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Integration Test Task"
        assert tasks[0].priority == "Hoch"
        
        # 2. Als erledigt markieren
        task_id = tasks[0].id
        state[f"done_{task_id}"] = True
        controller.toggle_done(task_id)
        
        task = controller.list_tasks()[0]
        assert task.done is True
        
        # 3. Löschen
        controller.delete_task(task_id)
        
        assert len(controller.list_tasks()) == 0

    def test_category_affects_tasks(self, system):
        """
        Test 2: Kategorie-Änderungen wirken sich auf Tasks aus.
        
        Prüft: Kategorien-Management über alle Schichten
        """
        controller, state = system
        
        # 1. Kategorie erstellen
        state["cat_new_name"] = "Arbeit"
        controller.add_category()
        
        assert "Arbeit" in controller.list_categories()
        
        # 2. Task mit Kategorie erstellen
        state["new_title"] = "Projekt abschließen"
        state["new_category"] = "Arbeit"
        controller.add_task()
        
        task = controller.list_tasks()[0]
        assert task.category == "Arbeit"
        
        # 3. Kategorie umbenennen → Task wird aktualisiert
        controller.start_rename_category("Arbeit")
        state["cat_rename_value"] = "Beruf"
        controller.save_rename_category("Arbeit")
        
        task = controller.list_tasks()[0]
        assert task.category == "Beruf"
        
        # 4. Kategorie löschen → Task-Kategorie wird None
        controller.delete_category("Beruf")
        
        task = controller.list_tasks()[0]
        assert task.category is None

    def test_filter_with_mixed_tasks(self, system):
        """
        Test 3: Filter funktioniert mit gemischten Task-Stati.
        
        Prüft: Filter-Logik über Controller und Service
        """
        controller, state = system
        
        # Tasks erstellen
        for title in ["Task A", "Task B", "Task C"]:
            state["new_title"] = title
            controller.add_task()
        
        # Task B als erledigt markieren
        tasks = controller.list_tasks()
        task_b = next(t for t in tasks if t.title == "Task B")
        state[f"done_{task_b.id}"] = True
        controller.toggle_done(task_b.id)
        
        # Filter testen
        controller.set_filter("Alle")
        assert len(controller.get_filtered_tasks()) == 3
        
        controller.set_filter("Offen")
        filtered = controller.get_filtered_tasks()
        assert len(filtered) == 2
        assert all(not t.done for t in filtered)
        
        controller.set_filter("Erledigt")
        filtered = controller.get_filtered_tasks()
        assert len(filtered) == 1
        assert filtered[0].title == "Task B"

    def test_edit_task_workflow(self, system):
        """
        Test 4: Task-Bearbeitung über UI-State.
        
        Prüft: Edit-Workflow Controller ↔ UI-State ↔ Service
        """
        controller, state = system
        
        # Task erstellen
        state["new_title"] = "Original Titel"
        state["new_priority"] = "Niedrig"
        controller.add_task()
        
        task = controller.list_tasks()[0]
        original_id = task.id
        
        # Bearbeitung starten
        controller.start_edit(
            task.id,
            task.title,
            task.due_date,
            task.category,
            task.priority,
        )
        
        assert controller.is_editing(task.id)
        
        # Werte im State ändern
        state[f"title_{task.id}"] = "Neuer Titel"
        state[f"prio_{task.id}"] = "Hoch"
        state[f"due_value_{task.id}"] = date(2025, 6, 15)
        
        # Speichern
        controller.save_edit(task.id)
        
        # Prüfen
        updated = controller.list_tasks()[0]
        assert updated.id == original_id
        assert updated.title == "Neuer Titel"
        assert updated.priority == "Hoch"
        assert updated.due_date == date(2025, 6, 15)
        assert not controller.is_editing(task.id)
