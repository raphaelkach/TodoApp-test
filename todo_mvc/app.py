from __future__ import annotations

from datetime import date
import streamlit as st

from controller.todo_controller import TodoController
from model.repository import SessionStateTaskRepository
from model.service import TodoService

st.set_page_config(page_title="Todo-App", layout="centered")
st.title("Todo-App")

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

CATEGORY_NONE_LABEL = "Kategorie auswählen"
FILTER_RAW_VALUES = {"Alle", "Offen", "Erledigt"}

# ---------- MVC Wiring ----------
repo = SessionStateTaskRepository(st.session_state)
service = TodoService(repo)
controller = TodoController(service)
controller.initialize()

# ---------- UI State ----------
st.session_state.setdefault("editing_id", None)

# Add form state
st.session_state.setdefault("new_title", "")
st.session_state.setdefault("add_due_date", None)
st.session_state.setdefault("new_category", CATEGORY_NONE_LABEL)

# Category management state
st.session_state.setdefault("cat_new_name", "")
st.session_state.setdefault("cat_rename_target", None)
st.session_state.setdefault("cat_rename_value", "")
st.session_state.setdefault("open_cat_dialog", False)

# Filter state
st.session_state.setdefault("filter_raw", "Alle")


# ---------- Helpers ----------
def cats() -> list[str]:
    return controller.list_categories()


def normalize_cat(value: str) -> str | None:
    if not value or value == CATEGORY_NONE_LABEL:
        return None
    return value


def validate_category_value(key: str) -> None:
    options = set([CATEGORY_NONE_LABEL] + cats())
    if key in st.session_state and st.session_state[key] not in options:
        st.session_state[key] = CATEGORY_NONE_LABEL


def normalize_filter_from_label(label: str) -> str:
    s = (label or "").strip()
    if s.startswith("Offen"):
        return "Offen"
    if s.startswith("Erledigt"):
        return "Erledigt"
    if s.startswith("Alle"):
        return "Alle"
    if s in FILTER_RAW_VALUES:
        return s
    return "Alle"


def get_filter_raw() -> str:
    raw = st.session_state.get("filter_raw", "Alle")
    if raw in FILTER_RAW_VALUES:
        return raw
    for key in ("filter_seg", "filter_radio"):
        if key in st.session_state:
            return normalize_filter_from_label(str(st.session_state[key]))
    return "Alle"


# Category actions
def add_category() -> None:
    name = (st.session_state.get("cat_new_name") or "").strip()
    if not name:
        return
    controller.add_category(name)
    st.session_state["cat_new_name"] = ""


def start_rename_category(old: str) -> None:
    st.session_state["cat_rename_target"] = old
    st.session_state["cat_rename_value"] = old


def cancel_rename() -> None:
    st.session_state["cat_rename_target"] = None
    st.session_state["cat_rename_value"] = ""


def save_rename_category(old: str) -> None:
    new = (st.session_state.get("cat_rename_value") or "").strip()
    controller.rename_category(old, new)
    st.session_state["cat_rename_target"] = None
    st.session_state["cat_rename_value"] = ""

    if new and new != old:
        if st.session_state.get("new_category") == old:
            st.session_state["new_category"] = new
        for k in list(st.session_state.keys()):
            if k.startswith("cat_sel_") and st.session_state.get(k) == old:
                st.session_state[k] = new


def delete_category(name: str) -> None:
    controller.delete_category(name)

    if st.session_state.get("cat_rename_target") == name:
        cancel_rename()

    if st.session_state.get("new_category") == name:
        st.session_state["new_category"] = CATEGORY_NONE_LABEL
    for k in list(st.session_state.keys()):
        if k.startswith("cat_sel_") and st.session_state.get(k) == name:
            st.session_state[k] = CATEGORY_NONE_LABEL


@st.dialog("Kategorien verwalten")
def category_dialog() -> None:
    current = cats()
    can_add = len(current) < 5

    st.text_input("Neue Kategorie", key="cat_new_name",
                  placeholder="z.B. Uni, Haushalt …", disabled=not can_add)
    st.button("Anlegen", icon=":material/add:", type="primary", on_click=add_category,
              key="cat_add_btn", use_container_width=True, disabled=not can_add)
    if not can_add:
        st.caption("Maximal 5 Kategorien möglich.")

    st.divider()

    current = cats()
    if not current:
        st.info("Noch keine Kategorien vorhanden.")
        return

    rename_target = st.session_state.get("cat_rename_target")

    for i, c in enumerate(current):
        if rename_target == c:
            a, b, d = st.columns([0.70, 0.15, 0.15],
                                 vertical_alignment="center")
            with a:
                st.text_input("Umbenennen", key="cat_rename_value",
                              label_visibility="collapsed")
            with b:
                st.button("\u200b", icon=":material/save:", type="tertiary",
                          key=f"cat_save_{i}", on_click=save_rename_category, args=(c,), help="Speichern", use_container_width=True)
            with d:
                st.button(
                    "\u200b",
                    icon=":material/cancel:",
                    type="tertiary",
                    key=f"cat_cancel_{i}",
                    on_click=cancel_rename,
                    help="Abbrechen",
                    use_container_width=True,
                )
        else:
            a, b, d = st.columns([0.70, 0.15, 0.15],
                                 vertical_alignment="center")
            with a:
                st.write(c)
            with b:
                st.button("\u200b", icon=":material/edit:", type="tertiary",
                          key=f"cat_edit_{i}", on_click=start_rename_category, args=(c), help="Umbenennen", use_container_width=True)
            with d:
                st.button("\u200b", icon=":material/delete:", type="tertiary",
                          key=f"cat_del_{i}", on_click=delete_category, args=(c), help="Löschen", use_container_width=True)


# ---------- Task actions ----------
def add_from_state() -> None:
    title = (st.session_state.get("new_title") or "").strip()
    if not title:
        return

    due = st.session_state.get("add_due_date")
    category = normalize_cat(st.session_state.get(
        "new_category", CATEGORY_NONE_LABEL))
    controller.add(title, due, category)

    st.session_state["new_title"] = ""
    st.session_state["add_due_date"] = None
    st.session_state["new_category"] = CATEGORY_NONE_LABEL


def on_delete(task_id: int) -> None:
    controller.delete(task_id)


def on_toggle_done(task_id: int) -> None:
    controller.set_done(task_id, bool(
        st.session_state.get(f"done_{task_id}", False)))


def on_edit(task_id: int, current_title: str, current_due: date | None, current_cat: str | None) -> None:
    st.session_state["editing_id"] = task_id
    st.session_state[f"title_{task_id}"] = current_title
    st.session_state[f"due_{task_id}"] = current_due
    st.session_state[f"cat_sel_{task_id}"] = current_cat if current_cat else CATEGORY_NONE_LABEL


def on_save(task_id: int) -> None:
    controller.rename(task_id, st.session_state.get(f"title_{task_id}", ""))

    due = st.session_state.get(f"due_{task_id}")  # date | None
    controller.set_due_date(task_id, due)

    category = normalize_cat(st.session_state.get(
        f"cat_sel_{task_id}", CATEGORY_NONE_LABEL))
    controller.set_category(task_id, category)

    st.session_state["editing_id"] = None


def on_cancel(task_id: int, original_title: str, original_due: date | None, original_cat: str | None) -> None:
    st.session_state[f"title_{task_id}"] = original_title
    st.session_state[f"due_{task_id}"] = original_due
    st.session_state[f"cat_sel_{task_id}"] = original_cat if original_cat else CATEGORY_NONE_LABEL
    st.session_state["editing_id"] = None


col_add, col_list = st.columns([0.40, 0.60], gap="small")

# Neue Aufgabe (links)
with col_add:
    with st.container(border=True):
        h_left, h_right = st.columns([0.85, 0.15], vertical_alignment="center")
        with h_left:
            st.markdown("**Neue Aufgabe**")
        with h_right:
            sp, btnc = st.columns([0.55, 0.45], vertical_alignment="center")
            with btnc:
                if st.button("\u200b", icon=":material/settings:", type="tertiary", key="open_settings_btn", help="Kategorien verwalten"):
                    st.session_state["open_cat_dialog"] = True

        if st.session_state.get("open_cat_dialog"):
            category_dialog()
            st.session_state["open_cat_dialog"] = False

        st.text_input("Aufgabe", placeholder="z.B. Folien wiederholen …",
                      label_visibility="collapsed", key="new_title", on_change=add_from_state)

        c_dead, c_cat = st.columns([0.30, 0.70], vertical_alignment="bottom")
        with c_dead:
            st.date_input("Deadline", key="add_due_date", value=st.session_state.get(
                "add_due_date"), label_visibility="collapsed", format="DD.MM.YYYY")

        with c_cat:
            validate_category_value("new_category")
            available = cats()
            disabled = len(available) == 0

            st.selectbox("Kategorie", options=[CATEGORY_NONE_LABEL] + available if not disabled else [
                         CATEGORY_NONE_LABEL], key="new_category", label_visibility="collapsed", disabled=disabled)

        # Hinzufügen
        st.button("Hinzufügen", icon=":material/add_box:", type="primary",
                  on_click=add_from_state, key="add_btn", use_container_width=True)

# Aufgabenliste (rechts)
with col_list:
    with st.container(border=True):
        all_tasks = controller.list()
        all_count = len(all_tasks)
        open_count = sum(1 for t in all_tasks if not t.done)
        done_count = sum(1 for t in all_tasks if t.done)

        st.markdown("**Aufgabenliste**")

        opt_all = f"Alle ({all_count})"
        opt_open = f"Offen ({open_count})"
        opt_done = f"Erledigt ({done_count})"
        options = [opt_all, opt_open, opt_done]

        filter_raw = get_filter_raw()
        st.session_state["filter_raw"] = filter_raw

        if filter_raw == "Offen":
            default_opt = opt_open
        elif filter_raw == "Erledigt":
            default_opt = opt_done
        else:
            default_opt = opt_all

        if hasattr(st, "segmented_control"):
            selected = st.segmented_control(
                "Filter", options=options, default=default_opt, label_visibility="collapsed", key="filter_seg")
        else:
            selected = st.radio("Filter", options, index=options.index(
                default_opt), horizontal=True, label_visibility="collapsed", key="filter_radio")

        if selected is not None:
            st.session_state["filter_raw"] = normalize_filter_from_label(
                str(selected))

        filter_raw = get_filter_raw()
        if filter_raw == "Offen":
            tasks = [t for t in all_tasks if not t.done]
        elif filter_raw == "Erledigt":
            tasks = [t for t in all_tasks if t.done]
        else:
            tasks = all_tasks

        if not tasks:
            st.info("Noch keine Aufgaben.")
        else:
            for t in tasks:
                with st.container(border=True):
                    editing = (st.session_state.get("editing_id") == t.id)

                    if editing:
                        col_chk, col_main, col_save, col_cancel = st.columns(
                            [0.06, 0.82, 0.06, 0.06], gap="small", vertical_alignment="center")
                    else:
                        col_chk, col_main, col_edit, col_del = st.columns(
                            [0.06, 0.82, 0.06, 0.06], gap="small", vertical_alignment="center")

                    with col_chk:
                        st.checkbox(
                            "Erledigt", value=t.done, key=f"done_{t.id}", label_visibility="collapsed", on_change=on_toggle_done, args=(t.id))

                    with col_main:
                        left, right = st.columns(
                            [0.62, 0.38], vertical_alignment="bottom")

                        if editing:
                            st.session_state.setdefault(
                                f"title_{t.id}", t.title)
                            st.session_state.setdefault(
                                f"due_{t.id}", t.due_date)
                            st.session_state.setdefault(
                                f"cat_sel_{t.id}", t.category if t.category else CATEGORY_NONE_LABEL)

                            with left:
                                st.text_input(
                                    "Titel", key=f"title_{t.id}", label_visibility="collapsed")

                            with right:
                                r_dead, r_cat = st.columns(
                                    [0.42, 0.58], vertical_alignment="bottom")
                                with r_dead:
                                    st.date_input("Deadline", key=f"due_{t.id}", value=st.session_state.get(
                                        f"due_{t.id}"), label_visibility="collapsed", format="DD.MM.YYYY")
                                with r_cat:
                                    key = f"cat_sel_{t.id}"
                                    validate_category_value(key)
                                    available = cats()
                                    disabled = len(available) == 0
                                    st.selectbox("Kategorie", options=[CATEGORY_NONE_LABEL] + available if not disabled else [
                                                 CATEGORY_NONE_LABEL], key=key, label_visibility="collapsed", disabled=disabled)
                        else:
                            with left:
                                st.markdown(
                                    f"~~{t.title}~~" if t.done else t.title)
                            with right:
                                parts: list[str] = []
                                if t.due_date:
                                    parts.append(
                                        f"Deadline: {t.due_date.strftime('%d.%m.%Y')}")
                                if t.category:
                                    parts.append(t.category)
                                if parts:
                                    st.caption(" — ".join(parts))

                    if editing:
                        with col_save:
                            st.button("\u200b", icon=":material/save:", type="tertiary",
                                      help="Speichern", key=f"save_{t.id}", on_click=on_save, args=(t.id))
                        with col_cancel:
                            st.button("\u200b", icon=":material/cancel:", type="tertiary", help="Abbrechen",
                                      key=f"cancel_{t.id}", on_click=on_cancel, args=(t.id, t.title, t.due_date, t.category))
                    else:
                        with col_edit:
                            st.button("\u200b", icon=":material/edit:", type="tertiary", help="Bearbeiten",
                                      key=f"edit_{t.id}", on_click=on_edit, args=(t.id, t.title, t.due_date, t.category))
                        with col_del:
                            st.button("\u200b", icon=":material/delete_forever:", type="tertiary",
                                      help="Löschen", key=f"del_{t.id}", on_click=on_delete, args=(t.id))
