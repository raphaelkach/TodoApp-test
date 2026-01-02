import streamlit as st
from controller.todo_controller import TodoController
from model.repository import SessionStateTaskRepository
from model.service import TodoService

st.set_page_config(page_title="TODO-App", layout="centered")
st.title("TODO-App")

repo = SessionStateTaskRepository(st.session_state)
service = TodoService(repo)
controller = TodoController(service)

# Session State initialisieren
controller.initialize()

# Aufgaben hinzufügen
with st.form("add_form", clear_on_submit=True):
    title = st.text_input("Neue Aufgabe")
    if st.form_submit_button("Hinzufügen"):
        controller.add(title)
        # st.rerun() ist hier optional, Form-Submit triggert i.d.R. sowieso einen Rerun

st.divider()

# --- Aufgaben anzeigen + Löschen (dein neuer Block) ---
tasks = controller.list()

def on_delete(task_id: int):
    controller.delete(task_id)

if not tasks:
    st.info("Noch keine Aufgaben.")
else:
    for t in tasks:
        left, right = st.columns([0.85, 0.15], vertical_alignment="center")

        with left:
            st.checkbox(t.title, value=False, disabled=True, key=f"chk_{t.id}")

        with right:
            st.button("🗑️", key=f"del_{t.id}", on_click=on_delete, args=(t.id,))