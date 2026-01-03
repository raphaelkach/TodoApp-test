from __future__ import annotations

import streamlit as st
from controller.todo_controller import TodoController
from model.repository import SessionStateTaskRepository
from model.service import TodoService

st.set_page_config(page_title="TODO-App", layout="centered")
st.title("TODO-App")

# ---------------- CSS: responsive + Form-Rahmen entfernen + Add-Icon ----------------
st.markdown(
    """
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:
    opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />

    <style>
      /* Responsive Padding (aus Vorlesung: Media Queries in Streamlit) */
      .block-container { padding-top: 2rem; }
      @media (max-width: 768px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1.25rem; }
        h1 { font-size: 2.2rem !important; }
      }
      @media (min-width: 1100px) {
        .block-container { max-width: 920px; }
      }

      /* Form-Rahmen entfernen (falls Streamlit ihn rendert) */
      div[data-testid="stForm"] { border: 0 !important; padding: 0 !important; }
      div[data-testid="stForm"] > div { padding: 0 !important; }

      /* Mobile: Add-Form-Spalten umbrechen (nur innerhalb der Form) */
      @media (max-width: 768px) {
        div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
        div[data-testid="stForm"] div[data-testid="column"] { flex: 1 1 100% !important; width: 100% !important; }
      }

      /* Icon vor dem PRIMARY Submit (bei uns: Hinzufügen) */
      button[kind="primary"]::before {
        font-family: "Material Symbols Outlined";
        content: "add_circle";
        font-size: 1.25em;
        margin-right: 0.35em;
        vertical-align: -0.15em;
        font-variation-settings: "FILL" 0, "wght" 500, "GRAD" 0, "opsz" 24;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- MVC Wiring ----------------
repo = SessionStateTaskRepository(st.session_state)
service = TodoService(repo)
controller = TodoController(service)
controller.initialize()

# ---------------- UI State (Edit Mode) ----------------
if "editing_id" not in st.session_state:
    st.session_state["editing_id"] = None

# ---------------- Callbacks ----------------
def on_delete(task_id: int) -> None:
    controller.delete(task_id)

def on_toggle(task_id: int) -> None:
    done_value = bool(st.session_state.get(f"done_{task_id}", False))
    controller.set_done(task_id, done_value)

def on_edit(task_id: int, current_title: str) -> None:
    st.session_state["editing_id"] = task_id
    st.session_state[f"edit_title_{task_id}"] = current_title

def on_cancel_edit() -> None:
    eid = st.session_state.get("editing_id")
    if eid is not None:
        st.session_state.pop(f"edit_title_{eid}", None)
    st.session_state["editing_id"] = None

def on_save_edit(task_id: int) -> None:
    new_title = st.session_state.get(f"edit_title_{task_id}", "")
    controller.rename(task_id, new_title)
    st.session_state.pop(f"edit_title_{task_id}", None)
    st.session_state["editing_id"] = None

# ---------------- Add Area (Enter-to-add) ----------------
with st.container(border=True):
    st.markdown("**Neue Aufgabe**")

    try:
        form = st.form("add_form", clear_on_submit=True, border=False)
    except TypeError:
        form = st.form("add_form", clear_on_submit=True)

    with form:
        col_in, col_btn = st.columns([0.80, 0.20], vertical_alignment="bottom")

        with col_in:
            title = st.text_input(
                "Aufgabe",
                placeholder="z.B. Folien wiederholen …",
                label_visibility="collapsed",
            )

        with col_btn:
            submitted = st.form_submit_button(
                "Hinzufügen",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            controller.add(title)

st.divider()

# ---------------- Filter (optional, aber nützlich) ----------------
filter_opt = st.radio(
    "Filter",
    ["Alle", "Offen", "Erledigt"],
    horizontal=True,
    label_visibility="collapsed",
)

tasks = controller.list()
if filter_opt == "Offen":
    tasks = [t for t in tasks if not t.done]
elif filter_opt == "Erledigt":
    tasks = [t for t in tasks if t.done]

st.subheader(f"Aufgaben ({len(tasks)})")

# ---------------- List: jede Aufgabe eigene Karte ----------------
if not tasks:
    st.info("Noch keine Aufgaben.")
else:
    for t in tasks:
        with st.container(border=True):
            editing = (st.session_state.get("editing_id") == t.id)

            col_chk, col_main, col_actions = st.columns(
                [0.08, 0.74, 0.18],
                vertical_alignment="center",
            )

            with col_chk:
                st.checkbox(
                    "Erledigt",
                    value=t.done,
                    key=f"done_{t.id}",
                    label_visibility="collapsed",
                    on_change=on_toggle,
                    args=(t.id,),
                )

            with col_main:
                if editing:
                    st.text_input(
                        "Titel",
                        key=f"edit_title_{t.id}",
                        label_visibility="collapsed",
                    )
                else:
                    st.markdown(f"~~{t.title}~~" if t.done else t.title)

            with col_actions:
                if editing:
                    c1, c2 = st.columns([0.5, 0.5], vertical_alignment="center")
                    with c1:
                        st.button(
                            "\u200b",
                            icon=":material/check:",
                            type="secondary",
                            help="Speichern",
                            key=f"save_{t.id}",
                            on_click=on_save_edit,
                            args=(t.id,),
                            use_container_width=True,
                        )
                    with c2:
                        st.button(
                            "\u200b",
                            icon=":material/close:",
                            type="tertiary",
                            help="Abbrechen",
                            key=f"cancel_{t.id}",
                            on_click=on_cancel_edit,
                            use_container_width=True,
                        )
                else:
                    c1, c2 = st.columns([0.5, 0.5], vertical_alignment="center")
                    with c1:
                        st.button(
                            "\u200b",
                            icon=":material/edit:",
                            type="tertiary",
                            help="Bearbeiten",
                            key=f"edit_{t.id}",
                            on_click=on_edit,
                            args=(t.id, t.title),
                            use_container_width=True,
                        )
                    with c2:
                        st.button(
                            "\u200b",
                            icon=":material/delete_forever:",
                            type="tertiary",
                            help="Löschen",
                            key=f"del_{t.id}",
                            on_click=on_delete,
                            args=(t.id,),
                            use_container_width=True,
                        )

        st.write("")