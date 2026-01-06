"""View-Schicht für die Todo-App UI-Darstellung."""

from __future__ import annotations

import streamlit as st

from controller.todo_controller import TodoController
from model.constants import (
    CATEGORY_NONE_LABEL,
    DEFAULT_PRIORITY,
    FILTER_ALL,
    FILTER_OPEN,
    FILTER_DONE,
    PRIORITY_OPTIONS,
    PRIO_ICONS,
    ICON_ADD,
    ICON_ADD_BOX,
    ICON_EDIT,
    ICON_DELETE,
    ICON_SAVE,
    ICON_CANCEL,
    ICON_SETTINGS,
)

# Layout-Konstanten
TITLE_META_SPLIT = [0.30, 0.70]
META_SPLIT = [0.35, 0.27, 0.38]
ROW_COLS = [0.035, 0.885, 0.08]

# Spacer-Berechnung
EMPTY_LIST_SPACER_REM = 6.5
EMPTY_INFO_EST_REM = 4.58
TASK_CARD_EST_REM = (EMPTY_LIST_SPACER_REM + EMPTY_INFO_EST_REM) / 2


def render_app(controller: TodoController) -> None:
    """Hauptfunktion zum Rendern der gesamten App."""
    st.title("Todo-App")

    col_add, col_list = st.columns([0.30, 0.70], gap="small")

    with col_add:
        _render_add_form(controller)

    with col_list:
        _render_task_list(controller)


def _render_add_form(controller: TodoController) -> None:
    """Rendert das Formular zum Hinzufügen neuer Aufgaben."""
    with st.container(border=True):
        st.write("**Neue Aufgabe**")

        # Kategorie-Dialog anzeigen falls offen
        if controller.is_category_dialog_open():
            _render_category_dialog(controller)
            controller.close_category_dialog()

        # Titel-Eingabe
        st.text_input(
            "Aufgabe",
            placeholder="z.B. Folien wiederholen …",
            label_visibility="collapsed",
            key="new_title",
        )

        # Deadline und Priorität
        col_dead, col_prio = st.columns([0.51, 0.49], vertical_alignment="bottom")
        with col_dead:
            st.date_input(
                "Deadline",
                key="add_due_date",
                value=None,
                label_visibility="collapsed",
                format="DD.MM.YYYY",
            )
        with col_prio:
            st.selectbox(
                "Priorität",
                options=PRIORITY_OPTIONS,
                key="new_priority",
                label_visibility="collapsed",
            )

        # Kategorie-Auswahl
        controller.validate_category_value("new_category")
        available = controller.list_categories()
        disabled = len(available) == 0

        col_cat, col_set = st.columns([0.88, 0.12], vertical_alignment="bottom")
        with col_cat:
            options = [CATEGORY_NONE_LABEL] + available if not disabled else [CATEGORY_NONE_LABEL]
            st.selectbox(
                "Kategorie",
                options=options,
                key="new_category",
                label_visibility="collapsed",
                disabled=disabled,
            )
        with col_set:
            if st.button(
                "\u200b",
                icon=ICON_SETTINGS,
                type="tertiary",
                key="open_settings_btn",
                help="Kategorien verwalten",
                use_container_width=True,
            ):
                controller.open_category_dialog()

        # Hinzufügen-Button
        st.button(
            "Hinzufügen",
            icon=ICON_ADD_BOX,
            type="primary",
            on_click=controller.add_task,
            key="add_btn",
            use_container_width=True,
        )


@st.dialog("Kategorien verwalten")
def _render_category_dialog(controller: TodoController) -> None:
    """Rendert den Dialog zur Kategorieverwaltung."""
    current = controller.list_categories()
    can_add = controller.can_add_category()

    # Neue Kategorie hinzufügen
    st.text_input(
        "Neue Kategorie",
        key="cat_new_name",
        placeholder="z.B. Uni, Haushalt …",
        disabled=not can_add,
    )
    st.button(
        "Anlegen",
        icon=ICON_ADD,
        type="primary",
        on_click=controller.add_category,
        key="cat_add_btn",
        use_container_width=True,
        disabled=not can_add,
    )
    if not can_add:
        st.caption("Maximal 5 Kategorien möglich.")

    st.divider()

    # Bestehende Kategorien anzeigen
    current = controller.list_categories()
    if not current:
        st.info("Noch keine Kategorien vorhanden.")
        return

    rename_target = controller.get_rename_target()

    for i, cat in enumerate(current):
        if rename_target == cat:
            _render_category_edit_row(controller, cat, i)
        else:
            _render_category_view_row(controller, cat, i)


def _render_category_edit_row(controller: TodoController, cat: str, index: int) -> None:
    """Rendert eine Kategorie-Zeile im Bearbeitungsmodus."""
    col_name, col_save, col_cancel = st.columns([0.70, 0.15, 0.15], vertical_alignment="center")

    with col_name:
        st.text_input("Umbenennen", key="cat_rename_value", label_visibility="collapsed")
    with col_save:
        st.button(
            "\u200b",
            icon=ICON_SAVE,
            type="tertiary",
            key=f"cat_save_{index}",
            on_click=controller.save_rename_category,
            args=(cat,),
            help="Speichern",
            use_container_width=True,
        )
    with col_cancel:
        st.button(
            "\u200b",
            icon=ICON_CANCEL,
            type="tertiary",
            key=f"cat_cancel_{index}",
            on_click=controller.cancel_rename_category,
            help="Abbrechen",
            use_container_width=True,
        )


def _render_category_view_row(controller: TodoController, cat: str, index: int) -> None:
    """Rendert eine Kategorie-Zeile im Ansichtsmodus."""
    col_name, col_edit, col_del = st.columns([0.70, 0.15, 0.15], vertical_alignment="center")

    with col_name:
        st.write(cat)
    with col_edit:
        st.button(
            "\u200b",
            icon=ICON_EDIT,
            type="tertiary",
            key=f"cat_edit_{index}",
            on_click=controller.start_rename_category,
            args=(cat,),
            help="Umbenennen",
            use_container_width=True,
        )
    with col_del:
        st.button(
            "\u200b",
            icon=ICON_DELETE,
            type="tertiary",
            key=f"cat_del_{index}",
            on_click=controller.delete_category,
            args=(cat,),
            help="Löschen",
            use_container_width=True,
        )


def _render_task_list(controller: TodoController) -> None:
    """Rendert die Aufgabenliste mit Filter."""
    with st.container(border=True):
        st.write("**Aufgabenliste**")

        # Filter rendern
        _render_filter(controller)

        # Tasks anzeigen
        tasks = controller.get_filtered_tasks()

        if not tasks:
            st.info("Noch keine Aufgaben.")
            _render_list_spacer(0)
        else:
            for task in tasks:
                _render_task_row(controller, task)
            _render_list_spacer(len(tasks))


def _render_filter(controller: TodoController) -> None:
    """Rendert die Filter-Segmente."""
    all_count, open_count, done_count = controller.get_task_counts()

    opt_all = f"Alle ({all_count})"
    opt_open = f"Offen ({open_count})"
    opt_done = f"Erledigt ({done_count})"
    options = [opt_all, opt_open, opt_done]

    filter_raw = controller.get_filter()

    if filter_raw == FILTER_OPEN:
        default_opt = opt_open
    elif filter_raw == FILTER_DONE:
        default_opt = opt_done
    else:
        default_opt = opt_all

    # Segmented Control wenn verfügbar, sonst Radio
    if hasattr(st, "segmented_control"):
        selected = st.segmented_control(
            "Filter",
            options=options,
            default=default_opt,
            label_visibility="collapsed",
            key="filter_seg",
        )
    else:
        selected = st.radio(
            "Filter",
            options,
            index=options.index(default_opt),
            horizontal=True,
            label_visibility="collapsed",
            key="filter_radio",
        )

    if selected is not None:
        controller.set_filter(str(selected))


def _render_task_row(controller: TodoController, task) -> None:
    """Rendert eine einzelne Task-Zeile."""
    with st.container(border=True):
        editing = controller.is_editing(task.id)

        col_chk, col_main, col_buttons = st.columns(
            ROW_COLS,
            gap="small",
            vertical_alignment="center",
        )

        # Checkbox
        with col_chk:
            st.checkbox(
                "\u200b",
                value=task.done,
                key=f"done_{task.id}",
                label_visibility="collapsed",
                on_change=controller.toggle_done,
                args=(task.id,),
                help="Als erledigt markieren",
            )

        # Hauptbereich (Titel + Meta)
        with col_main:
            if editing:
                _render_task_edit_content(controller, task)
            else:
                _render_task_view_content(task)

        # Buttons
        with col_buttons:
            if editing:
                _render_task_edit_buttons(controller, task)
            else:
                _render_task_view_buttons(controller, task)


def _render_task_view_content(task) -> None:
    """Rendert den Inhalt einer Task-Zeile im Ansichtsmodus."""
    title_area, meta_area = st.columns(
        TITLE_META_SPLIT,
        vertical_alignment="center",
        gap="small",
    )

    with title_area:
        if task.done:
            st.markdown(f"~~{task.title}~~")
        else:
            st.write(task.title)

    with meta_area:
        col_dead, col_prio, col_cat = st.columns(
            META_SPLIT,
            vertical_alignment="center",
            gap="small",
        )

        priority = getattr(task, "priority", DEFAULT_PRIORITY)

        with col_dead:
            st.caption(task.due_date.strftime("%d.%m.%Y") if task.due_date else "")
        with col_prio:
            icon = PRIO_ICONS.get(priority, PRIO_ICONS[DEFAULT_PRIORITY])
            st.caption(f"{icon} {priority}")
        with col_cat:
            st.caption(task.category or "")


def _render_task_edit_content(controller: TodoController, task) -> None:
    """Rendert den Inhalt einer Task-Zeile im Bearbeitungsmodus."""
    title_area, meta_area = st.columns(
        TITLE_META_SPLIT,
        vertical_alignment="bottom",
        gap="small",
    )

    # Initialwerte setzen
    st.session_state.setdefault(f"title_{task.id}", task.title)
    st.session_state.setdefault(f"prio_{task.id}", getattr(task, "priority", DEFAULT_PRIORITY))
    st.session_state.setdefault(
        f"cat_sel_{task.id}",
        task.category if task.category else CATEGORY_NONE_LABEL,
    )

    with title_area:
        st.text_input(
            "Titel",
            key=f"title_{task.id}",
            label_visibility="collapsed",
        )

    with meta_area:
        col_dead, col_prio, col_cat = st.columns(
            META_SPLIT,
            vertical_alignment="bottom",
            gap="small",
        )

        with col_dead:
            _render_due_date_input(controller, task)

        with col_prio:
            st.selectbox(
                "Priorität",
                PRIORITY_OPTIONS,
                key=f"prio_{task.id}",
                label_visibility="collapsed",
            )

        with col_cat:
            controller.validate_category_value(f"cat_sel_{task.id}")
            available = controller.list_categories()
            disabled = len(available) == 0
            options = [CATEGORY_NONE_LABEL] + available if not disabled else [CATEGORY_NONE_LABEL]

            st.selectbox(
                "Kategorie",
                options=options,
                key=f"cat_sel_{task.id}",
                label_visibility="collapsed",
                disabled=disabled,
            )


def _render_due_date_input(controller: TodoController, task) -> None:
    """Rendert das Deadline-Eingabefeld im Bearbeitungsmodus."""
    edit_session = controller.get_edit_session()
    due_key = f"due_input_{task.id}_{edit_session}"
    init_key = f"due_value_{task.id}"

    if init_key not in st.session_state:
        st.session_state[init_key] = task.due_date

    if due_key not in st.session_state:
        init_val = st.session_state.get(init_key)
        if init_val is not None:
            st.session_state[due_key] = init_val

    st.date_input(
        "Deadline",
        key=due_key,
        value=None,
        label_visibility="collapsed",
        format="DD.MM.YYYY",
    )

    st.session_state[init_key] = st.session_state.get(due_key)


def _render_task_view_buttons(controller: TodoController, task) -> None:
    """Rendert die Buttons im Ansichtsmodus."""
    btn1, _gap, btn2 = st.columns([0.35, 0.05, 0.6], gap="small")

    priority = getattr(task, "priority", DEFAULT_PRIORITY)

    with btn1:
        st.button(
            "\u200b",
            icon=ICON_EDIT,
            type="tertiary",
            help="Bearbeiten",
            key=f"edit_{task.id}",
            on_click=controller.start_edit,
            args=(task.id, task.title, task.due_date, task.category, priority),
        )
    with btn2:
        st.button(
            "\u200b",
            icon=ICON_DELETE,
            type="tertiary",
            help="Löschen",
            key=f"del_{task.id}",
            on_click=controller.delete_task,
            args=(task.id,),
        )


def _render_task_edit_buttons(controller: TodoController, task) -> None:
    """Rendert die Buttons im Bearbeitungsmodus."""
    btn1, _gap, btn2 = st.columns([0.35, 0.05, 0.6], gap="small")

    priority = getattr(task, "priority", DEFAULT_PRIORITY)

    with btn1:
        st.button(
            "\u200b",
            icon=ICON_SAVE,
            type="tertiary",
            help="Speichern",
            key=f"save_{task.id}",
            on_click=controller.save_edit,
            args=(task.id,),
        )
    with btn2:
        st.button(
            "\u200b",
            icon=ICON_CANCEL,
            type="tertiary",
            help="Abbrechen",
            key=f"cancel_{task.id}",
            on_click=controller.cancel_edit,
            args=(task.id, task.title, task.due_date, task.category, priority),
        )


def _render_list_spacer(displayed_count: int) -> None:
    """Rendert einen Spacer für konsistente Listenhöhe."""
    if displayed_count > 2:
        return

    if displayed_count == 0:
        rem = EMPTY_LIST_SPACER_REM
    else:
        rem = (EMPTY_LIST_SPACER_REM + EMPTY_INFO_EST_REM) - (displayed_count * TASK_CARD_EST_REM)

    if rem > 0:
        st.markdown(f"<div style='height:{rem}rem;'></div>")
