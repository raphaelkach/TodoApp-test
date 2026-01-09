"""
Integrationstests für die Todo-App.

Diese Tests prüfen das Zusammenspiel von Repository- und Service-Schicht.
"""

from __future__ import annotations

from datetime import date

import pytest

from model.entities import Task
from model.repository import SessionStateTaskRepository
from model.service import TodoService


@pytest.fixture
def mock_state():
    """Fixture für einen Mock Session State."""
    return {}


@pytest.fixture
def repository(mock_state):
    """Fixture für ein Repository mit Mock State."""
    return SessionStateTaskRepository(mock_state)


@pytest.fixture
def service(repository):
    """Fixture für einen Service mit Repository."""
    svc = TodoService(repository)
    svc.initialize()
    return svc


class TestTaskIntegration:
    """Integrationstests für Task-Operationen durch Repository und Service."""

    def test_create_multiple_tasks_and_verify_repository_consistency(
        self, service: TodoService, repository: SessionStateTaskRepository
    ) -> None:
        """
        Test: Mehrere Aufgaben erstellen und Repository-Konsistenz prüfen.
        
        Prüft:
        - IDs werden korrekt inkrementiert
        - Alle Tasks werden im Repository gespeichert
        - Task-Attribute werden korrekt übernommen
        - Service-Validierung funktioniert mit Repository zusammen
        """
        # Erstelle 3 verschiedene Tasks
        result1 = service.add_task(
            title="Erste Aufgabe",
            due_date=date(2026, 1, 15),
            priority="Hoch"
        )
        assert result1 is True

        result2 = service.add_task(
            title="Zweite Aufgabe",
            category=None,
            priority="Mittel"
        )
        assert result2 is True

        result3 = service.add_task(
            title="Dritte Aufgabe",
            due_date=date(2026, 1, 20),
            priority="Niedrig"
        )
        assert result3 is True

        # Prüfe Repository-Konsistenz
        all_tasks = repository.list_all()
        assert len(all_tasks) == 3

        # Prüfe IDs sind aufsteigend und eindeutig
        ids = [task.id for task in all_tasks]
        assert ids == [1, 2, 3]

        # Prüfe Task-Details
        task1 = all_tasks[0]
        assert task1.title == "Erste Aufgabe"
        assert task1.due_date == date(2026, 1, 15)
        assert task1.priority == "Hoch"
        assert task1.done is False

        task2 = all_tasks[1]
        assert task2.title == "Zweite Aufgabe"
        assert task2.priority == "Mittel"
        assert task2.category is None

        task3 = all_tasks[2]
        assert task3.title == "Dritte Aufgabe"
        assert task3.due_date == date(2026, 1, 20)
        assert task3.priority == "Niedrig"

    def test_update_task_status_updates_repository(
        self, service: TodoService, repository: SessionStateTaskRepository
    ) -> None:
        """
        Test: Status einer Aufgabe ändern und Repository-Aktualisierung prüfen.
        
        Prüft:
        - Task-Status wird über Service korrekt aktualisiert
        - Änderung wird im Repository persistent gespeichert
        - Andere Task-Attribute bleiben unverändert
        """
        # Erstelle einen Task
        service.add_task(
            title="Test Aufgabe",
            due_date=date(2026, 2, 1),
            priority="Mittel"
        )

        # Hole Task aus Repository
        tasks = repository.list_all()
        assert len(tasks) == 1
        task = tasks[0]
        task_id = task.id

        # Ursprünglicher Status sollte False sein
        assert task.done is False

        # Ändere Status über Service
        service.set_done(task_id, True)

        # Prüfe Repository direkt
        updated_tasks = repository.list_all()
        assert len(updated_tasks) == 1
        updated_task = updated_tasks[0]

        # Status sollte aktualisiert sein
        assert updated_task.done is True

        # Andere Attribute sollten unverändert sein
        assert updated_task.id == task_id
        assert updated_task.title == "Test Aufgabe"
        assert updated_task.due_date == date(2026, 2, 1)
        assert updated_task.priority == "Mittel"

        # Ändere Status zurück
        service.set_done(task_id, False)

        # Erneut prüfen
        final_tasks = repository.list_all()
        final_task = final_tasks[0]
        assert final_task.done is False

    def test_add_empty_task_fails_gracefully(
        self, service: TodoService, repository: SessionStateTaskRepository
    ) -> None:
        """
        Test: Leere Aufgabe erstellen schlägt kontrolliert fehl.
        
        Prüft:
        - Service validiert leere Titel und gibt False zurück
        - Keine invaliden Tasks werden im Repository gespeichert
        - Repository bleibt konsistent nach fehlgeschlagenen Operationen
        """
        # Versuche Tasks mit leerem/ungültigem Titel zu erstellen
        result1 = service.add_task(title="")
        assert result1 is False

        result2 = service.add_task(title="   ")  # Nur Leerzeichen
        assert result2 is False

        result3 = service.add_task(title=None)
        assert result3 is False

        # Repository sollte leer sein
        tasks = repository.list_all()
        assert len(tasks) == 0

        # Erstelle einen gültigen Task
        result4 = service.add_task(title="Gültige Aufgabe")
        assert result4 is True

        # Repository sollte genau einen Task enthalten
        tasks = repository.list_all()
        assert len(tasks) == 1
        assert tasks[0].title == "Gültige Aufgabe"

        # Versuche erneut einen leeren Task hinzuzufügen
        result5 = service.add_task(title="")
        assert result5 is False

        # Repository sollte immer noch nur einen Task haben
        tasks = repository.list_all()
        assert len(tasks) == 1


class TestCategoryIntegration:
    """Integrationstests für Kategorie-Operationen."""

    def test_delete_task_removes_from_repository(
        self, service: TodoService, repository: SessionStateTaskRepository
    ) -> None:
        """
        Bonus-Test: Task löschen entfernt ihn aus dem Repository.
        
        Prüft:
        - Gelöschte Tasks verschwinden aus dem Repository
        - Andere Tasks bleiben erhalten
        """
        # Erstelle mehrere Tasks
        service.add_task(title="Task 1")
        service.add_task(title="Task 2")
        service.add_task(title="Task 3")

        tasks = repository.list_all()
        assert len(tasks) == 3

        # Lösche mittleren Task
        task_id_to_delete = tasks[1].id
        service.delete_task(task_id_to_delete)

        # Prüfe Repository
        remaining_tasks = repository.list_all()
        assert len(remaining_tasks) == 2

        # Gelöschter Task sollte nicht mehr vorhanden sein
        remaining_ids = [t.id for t in remaining_tasks]
        assert task_id_to_delete not in remaining_ids

        # Andere Tasks sollten erhalten bleiben
        assert remaining_tasks[0].title == "Task 1"
        assert remaining_tasks[1].title == "Task 3"