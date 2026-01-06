"""Haupteinstiegspunkt der Todo-App."""

from __future__ import annotations

import streamlit as st

from controller.todo_controller import TodoController
from model.repository import SessionStateTaskRepository
from model.service import TodoService
from view.todo_view import render_app

# Page-Konfiguration
st.set_page_config(page_title="Todo-App", layout="wide")

# CSS nur wo unbedingt nötig (Responsive Design)
st.markdown(
    """
    <style>
      /* Responsive Padding - nicht mit Streamlit lösbar */
      .block-container { padding-top: 2rem; }

      @media (max-width: 768px) {
        .block-container {
          padding-left: 1rem;
          padding-right: 1rem;
          padding-top: 1.25rem;
        }
        h1 { font-size: 2.2rem !important; }
      }

      @media (min-width: 1100px) {
        .block-container { max-width: 1200px; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# MVC Wiring
repo = SessionStateTaskRepository(st.session_state)
service = TodoService(repo)
controller = TodoController(service, st.session_state)
controller.initialize()

# View rendern
render_app(controller)
