"""
Integrationstests für die Todo-App.

Tests für das Zusammenspiel von Repository und Service.
"""

from __future__ import annotations

from datetime import date

import pytest

from model.repository import SessionStateTaskRepository
from model.service import TodoService


@pytest.fixture
def mock_state():
    """Mock Session State."""
    return {}


@pytest.fixture
def repository(mock_state):
    """Repository mit Mock State."""
    return SessionStateTaskRepository(mock_state)


@pytest.fixture
def service(repository):
    """Service mit Repository."""
    svc = TodoService(repository)
    svc.initialize()
    return svc


class TestTaskIntegration:
    """Integrationstests für Task-Operationen."""

    def test_create_multiple_tasks_and_verify_repository_consistency(
        self, service: TodoService, repository: SessionStateTaskRepository
    ) -> None:
        """
        Test: Mehrere Aufgaben erstellen und Repository-Konsistenz prüfen.
        """
        # Erstellt 3 Tasks mit unterschiedlichen Attributen
        service.add_task(
            title="Erste Aufgabe",
            due_date=date(2026, 1, 15),
            priority="Hoch"
        )
        service.add_task(
            title="Zweite Aufgabe",
            priority="Mittel"
        )
        service.add_task(
            title="Dritte Aufgabe",
            due_date=date(2026, 1, 20),
            priority="Niedrig"
        )

        # Prüft Repository-Konsistenz
        all_tasks = repository.list_all()
        assert len(all_tasks) == 3

        # IDs sind aufsteigend
        ids = [task.id for task in all_tasks]
        assert ids == [1, 2, 3]

        # Attribute korrekt gespeichert
        assert all_tasks[0].title == "Erste Aufgabe"
        assert all_tasks[0].priority == "Hoch"
        assert all_tasks[0].done is False
        
        assert all_tasks[1].title == "Zweite Aufgabe"
        assert all_tasks[1].priority == "Mittel"
        
        assert all_tasks[2].title == "Dritte Aufgabe"
        assert all_tasks[2].due_date == date(2026, 1, 20)

    def test_update_task_status_updates_repository(
        self, service: TodoService, repository: SessionStateTaskRepository
    ) -> None:
        """
        Test: Status-Änderung wird im Repository aktualisiert.
        """
        # Task erstellen
        service.add_task(
            title="Test Aufgabe",
            due_date=date(2026, 2, 1),
            priority="Mittel"
        )

        task_id = repository.list_all()[0].id
        
        # Ursprünglicher Status: nicht erledigt
        assert repository.list_all()[0].done is False

        # Status ändern
        service.set_done(task_id, True)

        # Status im Repository aktualisiert
        updated_task = repository.list_all()[0]
        assert updated_task.done is True
        
        # Andere Attribute unverändert
        assert updated_task.title == "Test Aufgabe"
        assert updated_task.due_date == date(2026, 2, 1)
        assert updated_task.priority == "Mittel"

    def test_add_empty_task_fails_gracefully(
        self, service: TodoService, repository: SessionStateTaskRepository
    ) -> None:
        """
        Test: Leere Aufgaben werden kontrolliert abgelehnt.
        """
        # Ungültige Eingaben
        assert service.add_task(title="") is False
        assert service.add_task(title="   ") is False
        assert service.add_task(title=None) is False

        # Repository bleibt leer
        assert len(repository.list_all()) == 0

        # Gültige Aufgabe funktioniert
        assert service.add_task(title="Gültige Aufgabe") is True
        assert len(repository.list_all()) == 1
        
        # Weitere leere Eingabe wird abgelehnt
        assert service.add_task(title="") is False
        assert len(repository.list_all()) == 1