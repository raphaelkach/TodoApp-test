"""Controller für die Todo-App mit UI-State-Management."""

from __future__ import annotations

from datetime import date
from typing import List, MutableMapping

from model.entities import Task
from model.service import TodoService
from model.constants import (
    CATEGORY_NONE_LABEL,
    PRIORITY_NONE_LABEL,
    FILTER_ALL,
    FILTER_OPEN,
    FILTER_DONE,
    FILTER_OPTIONS,
    UI_EDITING_ID,
    UI_NEW_TITLE,
    UI_ADD_DUE_DATE,
    UI_NEW_PRIORITY,
    UI_NEW_CATEGORY,
    UI_FILTER_RAW,
    UI_CAT_NEW_NAME,
    UI_CAT_RENAME_TARGET,
    UI_CAT_RENAME_VALUE,
    UI_OPEN_CAT_DIALOG,
    UI_EDIT_SESSION,
)


class TodoController:
    """Controller zur Steuerung der Todo-App."""

    def __init__(self, service: TodoService, ui_state: MutableMapping) -> None:
        self._service = service
        self._ui = ui_state

    # ---------- Initialisierung ----------

    def initialize(self) -> None:
        """Initialisiert Service und UI-State."""
        self._service.initialize()
        self._init_ui_state()

    def _init_ui_state(self) -> None:
        """Initialisiert den UI-State mit Standardwerten."""
        defaults = {
            UI_EDITING_ID: None,
            UI_NEW_TITLE: "",
            UI_ADD_DUE_DATE: None,
            UI_NEW_PRIORITY: PRIORITY_NONE_LABEL,
            UI_NEW_CATEGORY: CATEGORY_NONE_LABEL,
            UI_FILTER_RAW: FILTER_ALL,
            UI_CAT_NEW_NAME: "",
            UI_CAT_RENAME_TARGET: None,
            UI_CAT_RENAME_VALUE: "",
            UI_OPEN_CAT_DIALOG: False,
            UI_EDIT_SESSION: 0,
        }
        for key, default in defaults.items():
            self._ui.setdefault(key, default)

    # ---------- Kategorien (Daten) ----------

    def list_categories(self) -> List[str]:
        """Gibt alle Kategorien zurück."""
        return self._service.list_categories()

    def can_add_category(self) -> bool:
        """Prüft ob eine weitere Kategorie hinzugefügt werden kann."""
        return self._service.can_add_category()

    # ---------- Kategorien (Aktionen) ----------

    def add_category(self) -> None:
        """Fügt eine neue Kategorie aus dem UI-State hinzu."""
        name = (self._ui.get(UI_CAT_NEW_NAME) or "").strip()
        if name and self._service.add_category(name):
            self._ui[UI_CAT_NEW_NAME] = ""

    def start_rename_category(self, old: str) -> None:
        """Startet den Umbenennen-Modus für eine Kategorie."""
        self._ui[UI_CAT_RENAME_TARGET] = old
        self._ui[UI_CAT_RENAME_VALUE] = old

    def cancel_rename_category(self) -> None:
        """Bricht das Umbenennen einer Kategorie ab."""
        self._ui[UI_CAT_RENAME_TARGET] = None
        self._ui[UI_CAT_RENAME_VALUE] = ""

    def save_rename_category(self, old: str) -> None:
        """Speichert die umbenannte Kategorie."""
        new = (self._ui.get(UI_CAT_RENAME_VALUE) or "").strip()
        if self._service.rename_category(old, new) and new and new != old:
            self._update_category_references(old, new)

        self._ui[UI_CAT_RENAME_TARGET] = None
        self._ui[UI_CAT_RENAME_VALUE] = ""

    def delete_category(self, name: str) -> None:
        """Löscht eine Kategorie."""
        self._service.delete_category(name)

        if self._ui.get(UI_CAT_RENAME_TARGET) == name:
            self.cancel_rename_category()

        self._clear_category_references(name)

    def _update_category_references(self, old: str, new: str) -> None:
        """Aktualisiert UI-Referenzen nach Kategorie-Umbenennung."""
        if self._ui.get(UI_NEW_CATEGORY) == old:
            self._ui[UI_NEW_CATEGORY] = new

        for key in list(self._ui.keys()):
            if key.startswith("cat_sel_") and self._ui.get(key) == old:
                self._ui[key] = new

    def _clear_category_references(self, name: str) -> None:
        """Entfernt UI-Referenzen nach Kategorie-Löschung."""
        if self._ui.get(UI_NEW_CATEGORY) == name:
            self._ui[UI_NEW_CATEGORY] = CATEGORY_NONE_LABEL

        for key in list(self._ui.keys()):
            if key.startswith("cat_sel_") and self._ui.get(key) == name:
                self._ui[key] = CATEGORY_NONE_LABEL

    def get_rename_target(self) -> str | None:
        """Gibt die Kategorie zurück, die gerade umbenannt wird."""
        return self._ui.get(UI_CAT_RENAME_TARGET)

    def open_category_dialog(self) -> None:
        """Öffnet den Kategorien-Dialog."""
        self._ui[UI_OPEN_CAT_DIALOG] = True

    def close_category_dialog(self) -> None:
        """Schließt den Kategorien-Dialog."""
        self._ui[UI_OPEN_CAT_DIALOG] = False

    def is_category_dialog_open(self) -> bool:
        """Prüft ob der Kategorien-Dialog offen ist."""
        return bool(self._ui.get(UI_OPEN_CAT_DIALOG))

    # ---------- Tasks (Daten) ----------

    def list_tasks(self) -> List[Task]:
        """Gibt alle Tasks zurück."""
        return self._service.list_tasks()

    def get_filtered_tasks(self) -> List[Task]:
        """Gibt Tasks gefiltert nach aktuellem Filter zurück."""
        filter_value = self.get_filter()
        return self._service.get_filtered_tasks(filter_value)

    def get_task_counts(self) -> tuple[int, int, int]:
        """Gibt (alle, offen, erledigt) Anzahlen zurück."""
        return self._service.get_task_counts()

    # ---------- Tasks (Aktionen) ----------

    def add_task(self) -> None:
        """Fügt einen neuen Task aus dem UI-State hinzu."""
        title = (self._ui.get(UI_NEW_TITLE) or "").strip()
        if not title:
            return

        due_date = self._ui.get(UI_ADD_DUE_DATE)
        category = self._ui_to_domain(self._ui.get(UI_NEW_CATEGORY))
        priority = self._ui_to_domain(self._ui.get(UI_NEW_PRIORITY))

        if self._service.add_task(title, due_date, category, priority):
            self._reset_add_form()

    def _reset_add_form(self) -> None:
        """Setzt das Hinzufügen-Formular zurück."""
        self._ui[UI_NEW_TITLE] = ""
        self._ui[UI_ADD_DUE_DATE] = None
        self._ui[UI_NEW_PRIORITY] = PRIORITY_NONE_LABEL
        self._ui[UI_NEW_CATEGORY] = CATEGORY_NONE_LABEL

    def delete_task(self, task_id: int) -> None:
        """Löscht einen Task."""
        self._service.delete_task(task_id)

    def toggle_done(self, task_id: int) -> None:
        """Wechselt den Erledigt-Status eines Tasks."""
        done = bool(self._ui.get(f"done_{task_id}", False))
        self._service.set_done(task_id, done)

    # ---------- Task Bearbeiten ----------

    def start_edit(
        self,
        task_id: int,
        current_title: str,
        current_due: date | None,
        current_cat: str | None,
        current_prio: str | None,
    ) -> None:
        """Startet den Bearbeitungsmodus für einen Task."""
        self._ui[UI_EDIT_SESSION] = self._ui.get(UI_EDIT_SESSION, 0) + 1
        self._ui[UI_EDITING_ID] = task_id
        self._ui[f"title_{task_id}"] = current_title
        self._ui[f"prio_{task_id}"] = current_prio if current_prio else PRIORITY_NONE_LABEL
        self._ui[f"cat_sel_{task_id}"] = current_cat or CATEGORY_NONE_LABEL
        self._ui[f"due_value_{task_id}"] = current_due

    def save_edit(self, task_id: int) -> None:
        """Speichert die Bearbeitung eines Tasks."""
        title = self._ui.get(f"title_{task_id}", "")
        due_date = self._ui.get(f"due_value_{task_id}")
        priority = self._ui_to_domain(self._ui.get(f"prio_{task_id}"))
        category = self._ui_to_domain(self._ui.get(f"cat_sel_{task_id}"))

        self._service.update_task(
            task_id,
            title=title,
            due_date=due_date,
            category=category,
            priority=priority,
            update_due_date=True,
            update_priority=True,
        )

        self._cleanup_edit_state(task_id)

    def cancel_edit(
        self,
        task_id: int,
        original_title: str,
        original_due: date | None,
        original_cat: str | None,
        original_prio: str | None,
    ) -> None:
        """Bricht die Bearbeitung ab und stellt Originalwerte wieder her."""
        self._ui[f"title_{task_id}"] = original_title
        self._ui[f"prio_{task_id}"] = original_prio if original_prio else PRIORITY_NONE_LABEL
        self._ui[f"cat_sel_{task_id}"] = original_cat or CATEGORY_NONE_LABEL
        self._cleanup_edit_state(task_id)

    def _cleanup_edit_state(self, task_id: int) -> None:
        """Bereinigt den Edit-State."""
        self._ui.pop(f"due_value_{task_id}", None)
        self._ui[UI_EDITING_ID] = None

    def is_editing(self, task_id: int) -> bool:
        """Prüft ob ein Task gerade bearbeitet wird."""
        return self._ui.get(UI_EDITING_ID) == task_id

    def get_edit_session(self) -> int:
        """Gibt die aktuelle Edit-Session-ID zurück."""
        return self._ui.get(UI_EDIT_SESSION, 0)

    # ---------- Filter ----------

    def get_filter(self) -> str:
        """Gibt den aktuellen Filter-Wert zurück."""
        raw = self._ui.get(UI_FILTER_RAW, FILTER_ALL)
        if raw in FILTER_OPTIONS:
            return raw

        for key in ("filter_seg", "filter_radio"):
            if key in self._ui:
                return self._normalize_filter(str(self._ui[key]))

        return FILTER_ALL

    def set_filter(self, value: str) -> None:
        """Setzt den Filter-Wert."""
        self._ui[UI_FILTER_RAW] = self._normalize_filter(value)

    def _normalize_filter(self, label: str) -> str:
        """Normalisiert einen Filter-Label zu einem Filter-Wert."""
        s = (label or "").strip()
        if s.startswith("Offen"):
            return FILTER_OPEN
        if s.startswith("Erledigt"):
            return FILTER_DONE
        if s.startswith("Alle"):
            return FILTER_ALL
        if s in FILTER_OPTIONS:
            return s
        return FILTER_ALL

    # ---------- UI-Domain-Mapping ----------

    def _ui_to_domain(self, value: str | None) -> str | None:
        """Konvertiert UI-Wert (z.B. 'Kategorie auswählen') zu Domain-Wert (None)."""
        if not value or value in (CATEGORY_NONE_LABEL, PRIORITY_NONE_LABEL):
            return None
        return value

    def validate_category_value(self, key: str) -> None:
        """Validiert einen Kategorie-Wert im UI-State."""
        options = set([CATEGORY_NONE_LABEL] + self.list_categories())
        if key in self._ui and self._ui[key] not in options:
            self._ui[key] = CATEGORY_NONE_LABEL

    def get_ui_value(self, key: str, default=None):
        """Gibt einen UI-State-Wert zurück."""
        return self._ui.get(key, default)

    def set_ui_value(self, key: str, value) -> None:
        """Setzt einen UI-State-Wert."""
        self._ui[key] = value