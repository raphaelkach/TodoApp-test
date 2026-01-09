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
        
    def test_toggle_done_status_multiple_times(self):
        """
        Szenario: Erledigt-Status wird mehrfach gewechselt.
        
        Prüft, dass der Status korrekt zwischen erledigt/nicht erledigt
        gewechselt werden kann.
        """
        # ARRANGE
        mock_state = {}
        repo = SessionStateTaskRepository(mock_state)
        service = TodoService(repo)
        service.initialize()
        
        # Aufgabe anlegen
        service.add_task("Toggle-Test Aufgabe", None, None, None)
        task_id = service.list_tasks()[0].id
        
        # ACT & ASSERT - Mehrfaches Wechseln des Status
        
        # Zunächst nicht erledigt
        task = service.list_tasks()[0]
        assert task.done is False, "Neue Aufgabe sollte nicht erledigt sein"
        
        # Auf erledigt setzen
        service.set_done(task_id, True)
        task = service.list_tasks()[0]
        assert task.done is True, "Aufgabe sollte erledigt sein"
        
        # Wieder auf nicht erledigt setzen
        service.set_done(task_id, False)
        task = service.list_tasks()[0]
        assert task.done is False, "Aufgabe sollte wieder nicht erledigt sein"
        
        # Erneut auf erledigt setzen
        service.set_done(task_id, True)
        task = service.list_tasks()[0]
        assert task.done is True, "Aufgabe sollte wieder erledigt sein"
        
    def test_multiple_tasks_independent_done_status(self):
        """
        Szenario: Mehrere Aufgaben haben unabhängige Erledigt-Status.
        
        Prüft, dass das Markieren einer Aufgabe als erledigt
        andere Aufgaben nicht beeinflusst.
        """
        # ARRANGE
        mock_state = {}
        repo = SessionStateTaskRepository(mock_state)
        service = TodoService(repo)
        service.initialize()
        
        # Drei Aufgaben anlegen
        service.add_task("Aufgabe 1", None, None, None)
        service.add_task("Aufgabe 2", None, None, None)
        service.add_task("Aufgabe 3", None, None, None)
        
        tasks = service.list_tasks()
        task1_id = tasks[0].id
        task2_id = tasks[1].id
        task3_id = tasks[2].id
        
        # ACT - Nur mittlere Aufgabe als erledigt markieren
        service.set_done(task2_id, True)
        
        # ASSERT - Status aller Aufgaben prüfen
        updated_tasks = service.list_tasks()
        
        task1 = next(t for t in updated_tasks if t.id == task1_id)
        task2 = next(t for t in updated_tasks if t.id == task2_id)
        task3 = next(t for t in updated_tasks if t.id == task3_id)
        
        assert task1.done is False, "Aufgabe 1 sollte nicht erledigt sein"
        assert task2.done is True, "Aufgabe 2 sollte erledigt sein"
        assert task3.done is False, "Aufgabe 3 sollte nicht erledigt sein"
        
    def test_done_status_persists_in_repository(self):
        """
        Szenario: Erledigt-Status bleibt im Repository persistent.
        
        Prüft, dass der Status auch nach mehreren Service-Operationen
        korrekt im Repository gespeichert bleibt.
        """
        # ARRANGE
        mock_state = {}
        repo = SessionStateTaskRepository(mock_state)
        service = TodoService(repo)
        service.initialize()
        
        # Aufgabe anlegen
        service.add_task("Persistenz-Test", date(2026, 2, 1), None, "Mittel")
        task_id = service.list_tasks()[0].id
        
        # ACT - Als erledigt markieren
        service.set_done(task_id, True)
        
        # ASSERT - Status direkt im Repository prüfen
        repo_tasks = repo.list_all()
        assert len(repo_tasks) == 1
        assert repo_tasks[0].done is True, "Status sollte im Repository gespeichert sein"
        
        # ACT - Andere Attribute aktualisieren
        repo.update(task_id, title="Neuer Titel")
        
        # ASSERT - Done-Status sollte erhalten bleiben
        repo_tasks = repo.list_all()
        assert repo_tasks[0].done is True, "Done-Status sollte nach Update erhalten bleiben"
        assert repo_tasks[0].title == "Neuer Titel"
        
    def test_mark_task_with_category_as_done(self):
        """
        Szenario: Aufgabe mit Kategorie wird als erledigt markiert.
        
        Prüft, dass Kategorie und andere Attribute erhalten bleiben.
        """
        # ARRANGE
        mock_state = {}
        repo = SessionStateTaskRepository(mock_state)
        service = TodoService(repo)
        service.initialize()
        
        # Kategorie hinzufügen
        category_name = "Arbeit"
        service.add_category(category_name)
        
        # Aufgabe mit Kategorie anlegen
        service.add_task(
            title="Wichtiges Meeting",
            due_date=date(2026, 1, 20),
            category=category_name,
            priority="Hoch"
        )
        
        task_id = service.list_tasks()[0].id
        
        # ACT - Als erledigt markieren
        service.set_done(task_id, True)
        
        # ASSERT - Alle Attribute sollten erhalten bleiben
        task = service.list_tasks()[0]
        assert task.done is True
        assert task.title == "Wichtiges Meeting"
        assert task.category == category_name, "Kategorie sollte erhalten bleiben"
        assert task.due_date == date(2026, 1, 20), "Datum sollte erhalten bleiben"
        assert task.priority == "Hoch", "Priorität sollte erhalten bleiben"