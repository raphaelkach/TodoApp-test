"""
Systemtests für die Todo-App.

Testet das komplette System (Repository + Service) ohne UI.
"""

import pytest
from datetime import date

from model.repository import SessionStateTaskRepository
from model.service import TodoService


class TestMarkTaskAsDone:
    """
    Systemtest-Szenario: Aufgabe als erledigt markieren.
    
    Prüft, dass der Erledigt-Status einer Aufgabe korrekt
    im System gespeichert und abgerufen wird.
    """
    
    def test_mark_single_task_as_done(self):
        """
        Szenario: Eine neu angelegte Aufgabe wird als erledigt markiert.
        
        Schritte:
        1. System initialisieren (Repository + Service)
        2. Neue Aufgabe anlegen
        3. Initiale Prüfung: Aufgabe ist nicht erledigt
        4. Aufgabe als erledigt markieren
        5. Finale Prüfung: Status korrekt im System gespeichert
        """
        # ARRANGE - System aufsetzen
        mock_state = {}
        repo = SessionStateTaskRepository(mock_state)
        service = TodoService(repo)
        service.initialize()
        
        # ACT - Aufgabe anlegen
        task_title = "Systemtest durchführen"
        task_due = date(2026, 1, 15)
        task_priority = "Hoch"
        
        success = service.add_task(
            title=task_title,
            due_date=task_due,
            category=None,
            priority=task_priority
        )
        
        # ASSERT - Aufgabe erfolgreich angelegt
        assert success, "Aufgabe sollte erfolgreich angelegt werden"
        
        tasks = service.list_tasks()
        assert len(tasks) == 1, "Es sollte genau eine Aufgabe existieren"
        
        task = tasks[0]
        task_id = task.id
        
        # ASSERT - Initiale Prüfung: Aufgabe nicht erledigt
        assert task.title == task_title
        assert task.done is False, "Neue Aufgabe sollte nicht erledigt sein"
        assert task.due_date == task_due
        assert task.priority == task_priority
        
        # ACT - Aufgabe als erledigt markieren
        service.set_done(task_id, True)
        
        # ASSERT - Status im System prüfen
        updated_tasks = service.list_tasks()
        assert len(updated_tasks) == 1, "Anzahl der Aufgaben sollte unverändert sein"
        
        updated_task = updated_tasks[0]
        assert updated_task.id == task_id, "Task-ID sollte gleich bleiben"
        assert updated_task.title == task_title, "Titel sollte unverändert sein"
        assert updated_task.done is True, "Aufgabe sollte als erledigt markiert sein"
        assert updated_task.due_date == task_due, "Fälligkeitsdatum sollte unverändert sein"
        assert updated_task.priority == task_priority, "Priorität sollte unverändert sein"
        
    def test_toggle_done_status(self):
        """
        Szenario: Erledigt-Status wird mehrfach gewechselt.
        
        Prüft, dass der Status zwischen erledigt/nicht erledigt
        gewechselt werden kann und andere Attribute erhalten bleiben.
        """
        # ARRANGE
        mock_state = {}
        repo = SessionStateTaskRepository(mock_state)
        service = TodoService(repo)
        service.initialize()
        
        # Aufgabe mit allen Attributen anlegen
        service.add_task(
            title="Toggle-Test",
            due_date=date(2026, 2, 1),
            category=None,
            priority="Mittel"
        )
        task_id = service.list_tasks()[0].id
        
        # ACT & ASSERT - Mehrfaches Wechseln
        
        # Initial: nicht erledigt
        task = service.list_tasks()[0]
        assert task.done is False
        
        # Auf erledigt setzen
        service.set_done(task_id, True)
        task = service.list_tasks()[0]
        assert task.done is True
        assert task.title == "Toggle-Test"
        assert task.due_date == date(2026, 2, 1)
        assert task.priority == "Mittel"
        
        # Wieder auf nicht erledigt setzen
        service.set_done(task_id, False)
        task = service.list_tasks()[0]
        assert task.done is False
        assert task.title == "Toggle-Test"  # Attribute bleiben erhalten