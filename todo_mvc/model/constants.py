"""Zentrale Konstanten für die Todo-App."""

from __future__ import annotations

# Prioritäten
PRIORITIES: set[str] = {"Niedrig", "Mittel", "Hoch"}
PRIORITY_OPTIONS: list[str] = ["Niedrig", "Mittel", "Hoch"]
DEFAULT_PRIORITY: str = "Mittel"

# Kategorien
MAX_CATEGORIES: int = 5
CATEGORY_NONE_LABEL: str = "Kategorie wählen"

# Filter
FILTER_ALL: str = "Alle"
FILTER_OPEN: str = "Offen"
FILTER_DONE: str = "Erledigt"
FILTER_OPTIONS: set[str] = {FILTER_ALL, FILTER_OPEN, FILTER_DONE}

# Session State Keys
TASKS_KEY: str = "todos"
NEXT_ID_KEY: str = "next_id"
CATEGORIES_KEY: str = "categories"

# UI State Keys
UI_EDITING_ID: str = "editing_id"
UI_NEW_TITLE: str = "new_title"
UI_ADD_DUE_DATE: str = "add_due_date"
UI_NEW_PRIORITY: str = "new_priority"
UI_NEW_CATEGORY: str = "new_category"
UI_FILTER_RAW: str = "filter_raw"
UI_CAT_NEW_NAME: str = "cat_new_name"
UI_CAT_RENAME_TARGET: str = "cat_rename_target"
UI_CAT_RENAME_VALUE: str = "cat_rename_value"
UI_OPEN_CAT_DIALOG: str = "open_cat_dialog"
UI_EDIT_SESSION: str = "_edit_session"

# Icons (Google Material Icons)
ICON_ADD: str = ":material/add:"
ICON_ADD_CIRCLE: str = ":material/add_circle:"
ICON_EDIT: str = ":material/edit:"
ICON_DELETE: str = ":material/delete_forever:"
ICON_SAVE: str = ":material/save:"
ICON_CANCEL: str = ":material/cancel:"
ICON_SETTINGS: str = ":material/settings:"
ICON_PRIO_LOW: str = ":material/signal_cellular_1_bar:"
ICON_PRIO_MED: str = ":material/signal_cellular_2_bar:"
ICON_PRIO_HIGH: str = ":material/signal_cellular_4_bar:"

PRIO_ICONS: dict[str, str] = {
    "Niedrig": ICON_PRIO_LOW,
    "Mittel": ICON_PRIO_MED,
    "Hoch": ICON_PRIO_HIGH,
}