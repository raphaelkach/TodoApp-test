"""
Systemtests für die Todo-App.

Ziel: Prüfen, dass das komplette System technisch korrekt arbeitet,
inkl. Service, Repository und Controller (ohne echten Browser).

Framework: pytest

Szenarien:
- Aufgabe anlegen → geprüft wird Speicherung und Abruf
- Aufgabe als erledigt markieren → Status korrekt im System
- Aufgabe löschen → System konsistent
- Fehlerfälle → kontrollierte Fehlermeldung
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
def system() -> tuple[TodoController, MutableMapping]:
    """
    Erstellt ein vollständiges System (Repository → Service → Controller).
    Simuliert das komplette MVC-Setup wie in app.py.
    """
    state: MutableMapping = {}
    repo = SessionStateTaskRepository(state)
    service = TodoService(repo)
    controller = TodoController(service, state)
    controller.initialize()
    return controller, state


# ============================================================================
# Hilfsfunktionen zur UI-Simulation
# ============================================================================


def simulate_add_task(
    controller: TodoController,
    state: MutableMapping,
    title: str,
    priority: str = "Mittel",
    category: str | None = None,
    due_date: date | None = None,
) -> None:
    """Simuliert das Hinzufügen eines Tasks über die UI."""
    state["new_title"] = title
    state["new_priority"] = priority
    state["new_category"] = category or "Kategorie wählen"
    state["add_due_date"] = due_date
    controller.add_task()


def simulate_toggle_done(
    controller: TodoController,
    state: MutableMapping,
    task_id: int,
) -> None:
    """Simuliert das Togglen des Done-Status über die UI."""
    current_task = next((t for t in controller.list_tasks() if t.id == task_id), None)
    if current_task:
        state[f"done_{task_id}"] = not current_task.done
        controller.toggle_done(task_id)


# ============================================================================
# Systemtests
# ============================================================================


class TestSystem:
    """Systemtests für die Todo-App."""

    def test_create_task_stored_and_retrieved(self, system):
        """
        Systemtest 1: Aufgabe anlegen → Speicherung und Abruf geprüft.
        
        Prüft den kompletten Datenfluss:
        UI-State → Controller → Service → Repository → Session State
        """
        # Arrange
        controller, state = system
        
        # Act - Task über simulierte UI erstellen
        simulate_add_task(
            controller, state,
            title="Systemtest Aufgabe",
            priority="Hoch",
            due_date=date(2025, 12, 31),
        )
        
        # Assert - Task ist im System gespeichert
        tasks = controller.list_tasks()
        assert len(tasks) == 1, "Genau ein Task sollte existieren"
        
        task = tasks[0]
        assert task.title == "Systemtest Aufgabe"
        assert task.priority == "Hoch"
        assert task.due_date == date(2025, 12, 31)
        assert task.done is False
        
        # Assert - Task ist auch direkt im State (Persistenz)
        assert len(state["todos"]) == 1
        assert state["todos"][0].title == "Systemtest Aufgabe"

    def test_mark_task_done_status_correct(self, system):
        """
        Systemtest 2: Aufgabe als erledigt markieren → Status korrekt im System.
        
        Prüft, dass der Done-Status durch alle Schichten propagiert wird.
        """
        # Arrange
        controller, state = system
        simulate_add_task(controller, state, title="Zu erledigen")
        task_id = controller.list_tasks()[0].id
        
        # Act - Als erledigt markieren
        simulate_toggle_done(controller, state, task_id)
        
        # Assert - Status ist korrekt
        task = controller.list_tasks()[0]
        assert task.done is True, "Task sollte als erledigt markiert sein"
        
        # Assert - Status ist auch im State (Persistenz)
        assert state["todos"][0].done is True
        
        # Assert - Filter funktioniert korrekt
        controller.set_filter("Erledigt")
        filtered = controller.get_filtered_tasks()
        assert len(filtered) == 1
        assert filtered[0].id == task_id
        
        controller.set_filter("Offen")
        filtered = controller.get_filtered_tasks()
        assert len(filtered) == 0

    def test_delete_task_system_consistent(self, system):
        """
        Systemtest 3: Aufgabe löschen → System bleibt konsistent.
        
        Prüft, dass nach dem Löschen das System in einem validen Zustand ist.
        """
        # Arrange
        controller, state = system
        simulate_add_task(controller, state, title="Task 1")
        simulate_add_task(controller, state, title="Task 2")
        simulate_add_task(controller, state, title="Task 3")
        
        tasks = controller.list_tasks()
        assert len(tasks) == 3
        task_to_delete = tasks[1]  # Task 2
        
        # Act - Task löschen
        controller.delete_task(task_to_delete.id)
        
        # Assert - System ist konsistent
        remaining = controller.list_tasks()
        assert len(remaining) == 2, "Zwei Tasks sollten übrig sein"
        
        remaining_titles = [t.title for t in remaining]
        assert "Task 1" in remaining_titles
        assert "Task 3" in remaining_titles
        assert "Task 2" not in remaining_titles
        
        # Assert - State ist konsistent
        assert len(state["todos"]) == 2
        
        # Assert - Zähler sind korrekt
        all_c, open_c, done_c = controller.get_task_counts()
        assert all_c == 2
        assert open_c == 2
        assert done_c == 0

    def test_error_case_empty_title_controlled(self, system):
        """
        Systemtest 4: Fehlerfall leerer Titel → kontrollierte Behandlung.
        
        Prüft, dass ungültige Eingaben kontrolliert abgefangen werden,
        ohne Exceptions zu werfen.
        """
        # Arrange
        controller, state = system
        
        # Zuerst einen gültigen Task erstellen
        simulate_add_task(controller, state, title="Gültiger Task")
        initial_count = len(controller.list_tasks())
        
        # Act - Versuche leeren Task zu erstellen
        simulate_add_task(controller, state, title="")
        
        # Assert - Kein neuer Task wurde erstellt
        assert len(controller.list_tasks()) == initial_count, \
            "Bei leerem Titel sollte kein Task erstellt werden"
        
        # Act - Versuche Whitespace-only Task zu erstellen
        simulate_add_task(controller, state, title="   ")
        
        # Assert - Immer noch kein neuer Task
        assert len(controller.list_tasks()) == initial_count, \
            "Bei Whitespace-Titel sollte kein Task erstellt werden"
        
        # Act - Versuche Task mit ungültiger Priorität
        simulate_add_task(
            controller, state,
            title="Test mit ungültiger Prio",
            priority="SuperDringend",  # Ungültig
        )
        
        # Assert - Task wurde erstellt, aber mit Default-Priorität
        tasks = controller.list_tasks()
        assert len(tasks) == initial_count + 1
        new_task = tasks[-1]
        assert new_task.priority == "Mittel", \
            "Ungültige Priorität sollte auf Default gesetzt werden"
