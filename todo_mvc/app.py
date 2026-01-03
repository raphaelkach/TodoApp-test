from __future__ import annotations

from datetime import date
import streamlit as st

from controller.todo_controller import TodoController
from model.repository import SessionStateTaskRepository
from model.service import TodoService

st.set_page_config(page_title="TODO-App", layout="centered")
st.title("TODO-App")

# ------------------- DEIN CSS: MUSS GENAU SO BLEIBEN -------------------
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
st.session_state.setdefault("editing_id", None)

st.session_state.setdefault("new_title", "")
st.session_state.setdefault("add_due_enabled", False)
st.session_state.setdefault("add_due_date", date.today())

# ---------- Callbacks ----------
def add_from_state() -> None:
    title = (st.session_state.get("new_title") or "").strip()
    if not title:
        return

    due = st.session_state["add_due_date"] if st.session_state["add_due_enabled"] else None
    controller.add(title, due)

    st.session_state["new_title"] = ""
    st.session_state["add_due_enabled"] = False
    st.session_state["add_due_date"] = date.today()


def enable_add_due() -> None:
    st.session_state["add_due_enabled"] = True
    st.session_state["add_due_date"] = st.session_state.get("add_due_date") or date.today()


def clear_add_due() -> None:
    st.session_state["add_due_enabled"] = False
    st.session_state["add_due_date"] = date.today()


def on_delete(task_id: int) -> None:
    controller.delete(task_id)


def on_toggle_done(task_id: int) -> None:
    controller.set_done(task_id, bool(st.session_state.get(f"done_{task_id}", False)))


def on_edit(task_id: int, current_title: str, current_due: date | None) -> None:
    st.session_state["editing_id"] = task_id
    st.session_state[f"title_{task_id}"] = current_title
    st.session_state[f"due_enabled_{task_id}"] = current_due is not None
    st.session_state[f"due_{task_id}"] = current_due or date.today()


def enable_task_due(task_id: int) -> None:
    st.session_state[f"due_enabled_{task_id}"] = True
    st.session_state[f"due_{task_id}"] = st.session_state.get(f"due_{task_id}") or date.today()


def clear_task_due(task_id: int) -> None:
    st.session_state[f"due_enabled_{task_id}"] = False
    st.session_state[f"due_{task_id}"] = date.today()


def on_save(task_id: int) -> None:
    controller.rename(task_id, st.session_state.get(f"title_{task_id}", ""))

    enabled = bool(st.session_state.get(f"due_enabled_{task_id}", False))
    due = st.session_state.get(f"due_{task_id}", date.today()) if enabled else None
    controller.set_due_date(task_id, due)

    st.session_state["editing_id"] = None


def on_cancel(task_id: int, original_title: str, original_due: date | None) -> None:
    st.session_state[f"title_{task_id}"] = original_title
    st.session_state[f"due_enabled_{task_id}"] = original_due is not None
    st.session_state[f"due_{task_id}"] = original_due or date.today()
    st.session_state["editing_id"] = None


# ------------------- ADD: Titel + Deadline in einer Zeile -------------------
with st.container(border=True):
    st.markdown("**Neue Aufgabe**")

    col_title, col_due, col_add = st.columns([0.66, 0.16, 0.18], vertical_alignment="bottom")

    with col_title:
        st.text_input(
            "Aufgabe",
            placeholder="z.B. Folien wiederholen …",
            label_visibility="collapsed",
            key="new_title",
            on_change=add_from_state,
        )

    with col_due:
        if not st.session_state["add_due_enabled"]:
            st.button(
                "Deadline",
                icon=":material/event:",
                type="tertiary",
                on_click=enable_add_due,
                use_container_width=True,
                key="add_due_btn",
            )
        else:
            d1, d2 = st.columns([0.86, 0.14], vertical_alignment="bottom")
            with d1:
                st.date_input(
                    "Deadline",
                    key="add_due_date",
                    value=st.session_state["add_due_date"],
                    label_visibility="collapsed",
                    format="DD.MM.YYYY",
                )
            with d2:
                st.button(
                    "\u200b",
                    icon=":material/event_busy:",
                    type="tertiary",
                    help="Deadline entfernen",
                    on_click=clear_add_due,
                    use_container_width=True,
                    key="add_due_clear",
                )

    with col_add:
        st.button(
            "Hinzufügen",
            icon=":material/add_box:",
            type="primary",
            on_click=add_from_state,
            use_container_width=True,
            key="add_btn",
        )

st.divider()

# ---------- Filter + Counts ----------
all_tasks = controller.list()
open_count = sum(1 for t in all_tasks if not t.done)
done_count = sum(1 for t in all_tasks if t.done)

if hasattr(st, "segmented_control"):
    filter_opt = st.segmented_control(
        "Filter",
        options=["Alle", "Offen", "Erledigt"],
        default="Alle",
        label_visibility="collapsed",
        key="filter_seg",
    )
else:
    filter_opt = st.radio(
        "Filter",
        ["Alle", "Offen", "Erledigt"],
        horizontal=True,
        label_visibility="collapsed",
        key="filter_radio",
    )

tasks = all_tasks
if filter_opt == "Offen":
    tasks = [t for t in all_tasks if not t.done]
elif filter_opt == "Erledigt":
    tasks = [t for t in all_tasks if t.done]

st.subheader(f"Aufgaben ({len(tasks)}) · Offen: {open_count} · Erledigt: {done_count}")

# ------------------- LISTE: Titel + Deadline in einer Zeile -------------------
if not tasks:
    st.info("Noch keine Aufgaben.")
else:
    for t in tasks:
        with st.container(border=True):
            editing = (st.session_state.get("editing_id") == t.id)

            st.session_state.setdefault(f"title_{t.id}", t.title)
            st.session_state.setdefault(f"due_enabled_{t.id}", t.due_date is not None)
            st.session_state.setdefault(f"due_{t.id}", t.due_date or date.today())

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
                    on_change=on_toggle_done,
                    args=(t.id,),
                )

            with col_main:
                c_title, c_due = st.columns([0.80, 0.20], vertical_alignment="bottom")

                if editing:
                    with c_title:
                        st.text_input("Titel", key=f"title_{t.id}", label_visibility="collapsed")

                    with c_due:
                        if not st.session_state[f"due_enabled_{t.id}"]:
                            st.button(
                                "Deadline",
                                icon=":material/event:",
                                type="tertiary",
                                on_click=enable_task_due,
                                args=(t.id,),
                                use_container_width=True,
                                key=f"due_btn_{t.id}",
                            )
                        else:
                            d1, d2 = st.columns([0.86, 0.14], vertical_alignment="bottom")
                            with d1:
                                st.date_input(
                                    "Deadline",
                                    key=f"due_{t.id}",
                                    value=st.session_state[f"due_{t.id}"],
                                    label_visibility="collapsed",
                                    format="DD.MM.YYYY",
                                )
                            with d2:
                                st.button(
                                    "\u200b",
                                    icon=":material/event_busy:",
                                    type="tertiary",
                                    help="Deadline entfernen",
                                    on_click=clear_task_due,
                                    args=(t.id,),
                                    use_container_width=True,
                                    key=f"due_clear_{t.id}",
                                )

                else:
                    with c_title:
                        st.session_state[f"title_{t.id}"] = f"✓ {t.title}" if t.done else t.title
                        st.text_input("Titel", key=f"title_{t.id}", label_visibility="collapsed", disabled=True)

                    with c_due:
                        due_display = t.due_date.strftime("%d.%m.%y") if t.due_date else "—"
                        st.session_state[f"due_display_{t.id}"] = due_display
                        st.text_input("Deadline", key=f"due_display_{t.id}", label_visibility="collapsed", disabled=True)

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
                        args=(t.id, t.title, t.due_date),
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
                        args=(t.id, t.title, t.due_date),
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