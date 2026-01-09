"""
Haupteinstiegspunkt der Todo-App.

Responsive Design Features:
- Wide Layout für Desktop-Optimierung
- Automatisches Stacken von Spalten auf Mobile durch Streamlit
- CSS Media Queries für feinere Anpassungen
"""

from __future__ import annotations

import streamlit as st

from controller.todo_controller import TodoController
from model.repository import SessionStateTaskRepository
from model.service import TodoService
from view.todo_view import render_app

# Page-Konfiguration für responsive Darstellung
st.set_page_config(
    page_title="Todo-App",
    page_icon=":material/task_alt:",
    layout="wide",  # Nutzt verfügbare Bildschirmbreite
    initial_sidebar_state="collapsed",  # Sidebar standardmäßig eingeklappt
)

# MVC Wiring - Dependency Injection
repo = SessionStateTaskRepository(st.session_state)
service = TodoService(repo)
controller = TodoController(service)  # ✅ Kein ui_state mehr!
controller.initialize()

# View rendern (enthält responsive CSS)
render_app(controller)