from __future__ import annotations

import streamlit as st

from controller.todo_controller import TodoController
from model.repository import SessionStateTaskRepository
from model.service import TodoService
from view.todo_view import render_app

st.set_page_config(page_title="Todo-App", layout="wide")

# ------------------- DEIN CSS: (minimal angepasst: max-width) -------------------
st.markdown(
    """
    <style>
      .block-container { padding-top: 2rem; }
      @media (max-width: 768px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1.25rem; }
        h1 { font-size: 2.2rem !important; }
      }
      @media (min-width: 1100px) {
        .block-container { max-width: 1200px; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Minimal CSS: Checkbox horizontal + vertikal mittig ----
st.markdown(
    """
    <style>
      div[data-testid="stCheckbox"]{
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 0 !important;
        padding: 0 !important;
        transform: translateY(-2px);
      }

      div[data-testid="stCheckbox"] > label{
        margin: 0 !important;
        padding: 0 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- MVC Wiring ----------
repo = SessionStateTaskRepository(st.session_state)
service = TodoService(repo)
controller = TodoController(service)
controller.initialize()

# ---------- View ----------
render_app(controller)