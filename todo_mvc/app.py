from __future__ import annotations

import streamlit as st
from controller.todo_controller import TodoController
from model.repository import SessionStateTaskRepository
from model.service import TodoService

st.set_page_config(page_title="TODO-App", layout="centered")
st.title("TODO-App")

# ---------- Optional: kleines responsives Padding (kein Button-CSS) ----------
st.markdown(
    """
    <style>
      .block-container { padding-top: 2rem; }
      @media (max-width: 768px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1.25rem; }
        h1 { font-size: 2.2rem !important; }
      }
      @media (min-width: 1100px) {
        .block-container { max-width: 920px; }
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

# ---------- UI State ----------
if "editing_id" not in st.session_state:
    st.session_state["editing_id"] = None

if "new_title" not in st.session_state:
    st.session_state["new_title"] = ""

# ---------- Callbacks ----------
def add_from_state() -> None:
    title = (st.session_state.get("new_title") or "").strip()
    if title:
        controller.add(title)
    st.session_state["new_title"] = ""

def on_delete(task_id: int) -> None:
    controller.delete(task_id)

def on_toggle(task_id: int) -> None:
    done_value = bool(st.session_state.get(f"done_{task_id}", False))
    controller.set_done(task_id, done_value)

def on_edit(task_id: int, current_title: str) -> None:
    st.session_state["editing_id"] = task_id
    # Beim Editieren immer den "rohen" Titel ohne Prefix setzen
    st.session_state[f"title_{task_id}"] = current_title

def on_cancel_edit(task_id: int, current_title: str, done: bool) -> None:
    # Zurücksetzen auf Anzeige-Titel (mit Prefix, falls done)
    st.session_state[f"title_{task_id}"] = (f"✓ {current_title}" if done else current_title)
    st.session_state["editing_id"] = None

def on_save_edit(task_id: int) -> None:
    new_title = st.session_state.get(f"title_{task_id}", "")
    controller.rename(task_id, new_title)
    st.session_state["editing_id"] = None

# ---------- Add Area ----------
with st.container(border=True):
    st.markdown("**Neue Aufgabe**")

    col_in, col_btn = st.columns([0.80, 0.20], vertical_alignment="bottom")

    with col_in:
        st.text_input(
            "Aufgabe",
            placeholder="z.B. Folien wiederholen …",
            label_visibility="collapsed",
            key="new_title",
            on_change=add_from_state,  # ENTER -> hinzufügen
        )

    with col_btn:
        st.button(
            "Hinzufügen",
            icon=":material/add_box:",
            type="primary",
            help="Aufgabe hinzufügen",
            on_click=add_from_state,
            use_container_width=True,
        )

st.divider()

# ---------- Filter ----------
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

# ---------- List: jede Aufgabe eigene Karte ----------
if not tasks:
    st.info("Noch keine Aufgaben.")
else:
    for t in tasks:
        with st.container(border=True):
            editing = (st.session_state.get("editing_id") == t.id)
            title_key = f"title_{t.id}"

            # Im Nicht-Edit-Modus halten wir den Anzeigetext stabil im Session State
            if not editing:
                display_title = f"✓ {t.title}" if t.done else t.title
                st.session_state[title_key] = display_title
            else:
                # Im Edit-Modus sicherstellen, dass ein Wert vorhanden ist
                if title_key not in st.session_state:
                    st.session_state[title_key] = t.title

            if editing:
                col_chk, col_main, col_save, col_cancel = st.columns(
                    [0.06, 0.82, 0.06, 0.06],
                    gap="small",
                    vertical_alignment="center",
                )
            else:
                col_chk, col_main, col_edit, col_del = st.columns(
                    [0.06, 0.82, 0.06, 0.06],
                    gap="small",
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
                # ✅ Immer TextInput -> keine Höhen-/Padding-Änderung -> kein Springen
                st.text_input(
                    "Titel",
                    key=title_key,
                    label_visibility="collapsed",
                    disabled=not editing,
                )

            if editing:
                with col_save:
                    st.button(
                        "\u200b",
                        icon=":material/save:",
                        type="tertiary",  # ohne Rahmen
                        help="Speichern",
                        key=f"save_{t.id}",
                        on_click=on_save_edit,
                        args=(t.id,),
                    )

                with col_cancel:
                    st.button(
                        "\u200b",
                        icon=":material/cancel:",
                        type="tertiary",
                        help="Abbrechen",
                        key=f"cancel_{t.id}",
                        on_click=on_cancel_edit,
                        args=(t.id, t.title, t.done),
                    )

            else:
                with col_edit:
                    st.button(
                        "\u200b",
                        icon=":material/edit:",
                        type="tertiary",
                        help="Bearbeiten",
                        key=f"edit_{t.id}",
                        on_click=on_edit,
                        args=(t.id, t.title),
                    )

                with col_del:
                    st.button(
                        "\u200b",
                        icon=":material/delete_forever:",
                        type="tertiary",
                        help="Löschen",
                        key=f"del_{t.id}",
                        on_click=on_delete,
                        args=(t.id,),
                    )