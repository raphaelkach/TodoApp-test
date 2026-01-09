"""
Haupteinstiegspunkt der Todo-App.
"""

from __future__ import annotations

import streamlit as st

from controller.todo_controller import TodoController
from model.repository import SessionStateTaskRepository
from model.service import TodoService
from view.todo_view import render_app

# Page-Konfiguration

st.set_page_config(
    page_title="Todo-App",
    page_icon=":material/task_alt:",
    layout="wide",  # Nutzt verfügbare Bildschirmbreite
    initial_sidebar_state="collapsed",  # Sidebar standardmäßig eingeklappt
)

# MVC Wiring - Dependency Injection

# Repository-Schicht: Datenzugriff auf Session State
repo = SessionStateTaskRepository(st.session_state)

# Service-Schicht: Geschäftslogik und Validierung
service = TodoService(repo)

# Controller-Schicht: Koordination zwischen View und Service
controller = TodoController(service)

# Initialisiere Controller (erstellt Session State falls nötig)
controller.initialize()

# View Rendering
# View-Schicht: UI-Darstellung und Benutzerinteraktion
render_app(controller)