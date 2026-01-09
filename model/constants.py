"""Zentrale Konstanten für die Todo-App."""

from __future__ import annotations

# Prioritäten

# Erlaubte Prioritäts-Werte (für Validierung)
PRIORITIES: set[str] = {"Niedrig", "Mittel", "Hoch"}

# Prioritäts-Optionen in fester Reihenfolge (für UI-Dropdowns)
PRIORITY_OPTIONS: list[str] = ["Niedrig", "Mittel", "Hoch"]

# Default-Priorität für neue Aufgaben (None = keine Priorität)
DEFAULT_PRIORITY: str | None = None

# Kategorien

# Maximal erlaubte Anzahl von Kategorien
MAX_CATEGORIES: int = 5

# Filter
# Filter-Werte für die Aufgabenliste
FILTER_ALL: str = "Alle"
FILTER_OPEN: str = "Offen"
FILTER_DONE: str = "Erledigt"

# Erlaubte Filter-Werte (für Validierung)
FILTER_OPTIONS: set[str] = {FILTER_ALL, FILTER_OPEN, FILTER_DONE}

# Session State Keys
# Diese Keys werden für den Datenzugriff im Streamlit Session State verwendet

TASKS_KEY: str = "todos"          # Liste aller Tasks
NEXT_ID_KEY: str = "next_id"      # Nächste verfügbare Task-ID
CATEGORIES_KEY: str = "categories"  # Liste aller Kategorien

# Icons (Google Material Icons)
# Material Icons werden in Streamlit mit ":material/<name>:" referenziert

# Allgemeine Icons
ICON_ADD: str = ":material/add:"
ICON_ADD_CIRCLE: str = ":material/add_circle:"
ICON_EDIT: str = ":material/edit:"
ICON_DELETE: str = ":material/delete_forever:"
ICON_SAVE: str = ":material/save:"
ICON_CANCEL: str = ":material/cancel:"
ICON_SETTINGS: str = ":material/settings:"

# Prioritäts-Icons (Signalstärke-Metapher)
ICON_PRIO_LOW: str = ":material/signal_cellular_1_bar:"
ICON_PRIO_MED: str = ":material/signal_cellular_2_bar:"
ICON_PRIO_HIGH: str = ":material/signal_cellular_4_bar:"

# Mapping: Priorität -> Icon (für UI-Darstellung)
PRIO_ICONS: dict[str, str] = {
    "Niedrig": ICON_PRIO_LOW,
    "Mittel": ICON_PRIO_MED,
    "Hoch": ICON_PRIO_HIGH,
}