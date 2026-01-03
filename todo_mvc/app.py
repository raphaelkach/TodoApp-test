from __future__ import annotations

import streamlit as st
from controller.todo_controller import TodoController
from model.repository import SessionStateTaskRepository
from model.service import TodoService

st.set_page_config(page_title="TODO-App", layout="centered")
st.title("TODO-App")

# ---- CSS MUSS so bestehen bleiben (wie von dir vorgegeben) ----
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
    st.session_state[f"title_{task_id}"] = current_title  # roh (ohne ✓)

def on_save(task_id: int) -> None:
    controller.rename(task_id, st.session_state.get(f"title_{task_id}", ""))
    st.session_state["editing_id"] = None

def on_cancel(task_id: int, original_title: str) -> None:
    # zurücksetzen
    st.session_state[f"title_{task_id}"] = original_title
    st.session_state["editing_id"] = None

# ---------- Add Area (Enter + Button, ohne Form, Icon nativ) ----------
with st.container(border=True):
    st.markdown("**Neue Aufgabe**")

    col_in, col_btn = st.columns([0.82, 0.18], vertical_alignment="bottom")

    with col_in:
        st.text_input(
            "Aufgabe",
            placeholder="z.B. Folien wiederholen …",
            label_visibility="collapsed",
            key="new_title",
            on_change=add_from_state,   # Enter -> hinzufügen
        )

    with col_btn:
        st.button(
            "Hinzufügen",
            icon=":material/add_box:",
            type="primary",
            on_click=add_from_state,
            use_container_width=True,
        )

st.divider()

# ---------- Filter (Status) ----------
all_tasks = controller.list()
open_count = sum(1 for t in all_tasks if not t.done)
done_count = sum(1 for t in all_tasks if t.done)

# schöner: wenn segmented_control verfügbar, sonst radio
if hasattr(st, "segmented_control"):
    filter_opt = st.segmented_control(
        "Filter",
        options=["Alle", "Offen", "Erledigt"],
        default="Alle",
    )
else:
    filter_opt = st.radio(
        "Filter",
        ["Alle", "Offen", "Erledigt"],
        horizontal=True,
        label_visibility="collapsed",
    )

st.caption(f"Offen: **{open_count}** · Erledigt: **{done_count}**")

# Filter anwenden
tasks = all_tasks
if filter_opt == "Offen":
    tasks = [t for t in all_tasks if not t.done]
elif filter_opt == "Erledigt":
    tasks = [t for t in all_tasks if t.done]

st.subheader(f"Aufgaben ({len(tasks)})")

# ---------- List: jede Aufgabe eigene Karte, weniger Abstand (kein extra st.write) ----------
if not tasks:
    st.info("Noch keine Aufgaben.")
else:
    for t in tasks:
        with st.container(border=True):
            editing = (st.session_state.get("editing_id") == t.id)
            title_key = f"title_{t.id}"

            # stabiler Textwert im State (ohne Layout-Sprung)
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
                # gleicher Widget-Typ in beiden Zuständen -> kein Springen
                if editing:
                    st.text_input(
                        "Titel",
                        key=title_key,
                        label_visibility="collapsed",
                    )
                else:
                    # Anzeige als disabled TextInput (stabil, ohne CSS)
                    display = f"✓ {t.title}" if t.done else t.title
                    st.session_state[title_key] = display
                    st.text_input(
                        "Titel",
                        key=title_key,
                        label_visibility="collapsed",
                        disabled=True,
                    )

            if editing:
                with col_save:
                    st.button(
                        "\u200b",
                        icon=":material/save:",
                        type="tertiary",
                        help="Speichern",
                        key=f"save_{t.id}",
                        on_click=on_save,
                        args=(t.id,),
                    )
                with col_cancel:
                    st.button(
                        "\u200b",
                        icon=":material/cancel:",
                        type="tertiary",
                        help="Abbrechen",
                        key=f"cancel_{t.id}",
                        on_click=on_cancel,
                        args=(t.id, t.title),
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