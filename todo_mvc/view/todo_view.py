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
    ICON_ADD_CIRCLE,
    ICON_EDIT,
    ICON_DELETE,
    ICON_SAVE,
    ICON_CANCEL,
)

# Layout-Konstanten
TITLE_META_SPLIT = [0.30, 0.70]
META_SPLIT = [0.35, 0.27, 0.38]
ROW_COLS = [0.035, 0.885, 0.08]

# UI-Label für "Kategorien verwalten" direkt in der Kategorie-Selectbox
CAT_MANAGE_LABEL = "➕ Kategorien verwalten…"

# UI-Placeholder für Priorität
PRIO_PLACEHOLDER = "Priorität auswählen…"


def render_app(controller: TodoController) -> None:
    """Hauptfunktion zum Rendern der gesamten App."""
    st.title("Todo-App")

    # Oben: Neue Aufgabe (links) + KPI/Progress (rechts)
    col_add, col_kpi = st.columns([0.65, 0.35], gap="small")
    with col_add:
        _render_add_form(controller)
    with col_kpi:
        _render_kpi_panel(controller)

    # Unten: Aufgabenliste über volle Breite
    _render_task_list(controller)


def _render_kpi_panel(controller: TodoController) -> None:
    """Rendert KPI und Fortschritt (Erledigt-Progress) für Aufgaben."""
    all_count, open_count, done_count = controller.get_task_counts()
    percent_done = int(round((done_count / all_count) * 100)) if all_count else 0

    with st.container(border=True):
        st.write("**Fortschritt**")

        c1, c2, c3 = st.columns(3, gap="small")
        with c1:
            st.metric("Gesamt", all_count)
        with c2:
            st.metric("Offen", open_count)
        with c3:
            st.metric("Erledigt", done_count)

        st.caption(f"Erledigt: {done_count}/{all_count} ({percent_done}%)")
        st.progress(percent_done)


def _render_add_form(controller: TodoController) -> None:
    """Rendert das Formular zum Hinzufügen neuer Aufgaben."""
    with st.container(border=True):
        st.write("**Neue Aufgabe**")

        # Zeile 1: Titel + Deadline
        col_title, col_dead = st.columns([0.72, 0.28], vertical_alignment="bottom")
        with col_title:
            st.text_input(
                "Aufgabe",
                placeholder="z.B. Folien wiederholen …",
                label_visibility="collapsed",
                key="new_title",
            )
        with col_dead:
            st.date_input(
                "Deadline",
                key="add_due_date",
                value=None,
                label_visibility="collapsed",
                format="DD.MM.YYYY",
            )

        # Zeile 2: Priorität + Kategorie (inkl. "Kategorien verwalten…")
        col_prio, col_cat = st.columns([0.5, 0.5], vertical_alignment="bottom")

        with col_prio:
            # UI-Key getrennt vom echten Key, damit wir "Priorität auswählen…" anzeigen können
            prio_real_key = "new_priority"
            prio_ui_key = "new_priority_ui"

            # echtes Feld hat weiterhin einen sinnvollen Default (für Add-Logik)
            st.session_state.setdefault(prio_real_key, DEFAULT_PRIORITY)

            prio_options = [PRIO_PLACEHOLDER] + list(PRIORITY_OPTIONS)

            # UI initial: Placeholder (oder bereits gewählte Priorität)
            st.session_state.setdefault(prio_ui_key, PRIO_PLACEHOLDER)
            if st.session_state.get(prio_real_key) in PRIORITY_OPTIONS and st.session_state[prio_ui_key] == PRIO_PLACEHOLDER:
                # falls schon mal gesetzt, UI synchronisieren
                st.session_state[prio_ui_key] = st.session_state[prio_real_key]

            def _on_new_priority_change() -> None:
                sel = st.session_state.get(prio_ui_key, PRIO_PLACEHOLDER)
                if sel in PRIORITY_OPTIONS:
                    st.session_state[prio_real_key] = sel
                else:
                    # Placeholder ausgewählt -> echtes Feld bleibt Default
                    st.session_state[prio_real_key] = DEFAULT_PRIORITY

            st.selectbox(
                "Priorität",
                options=prio_options,
                key=prio_ui_key,
                label_visibility="collapsed",
                on_change=_on_new_priority_change,
            )

        with col_cat:
            # Realer Wert (den Controller später nutzt) und UI-Key (Selectbox)
            real_key = "new_category"
            ui_key = "new_category_ui"

            # Defaults setzen + validieren
            st.session_state.setdefault(real_key, CATEGORY_NONE_LABEL)
            controller.validate_category_value(real_key)

            available = controller.list_categories()
            cat_options = [CATEGORY_NONE_LABEL] + available + [CAT_MANAGE_LABEL]

            # UI-Auswahl initial mit realem Wert synchronisieren
            st.session_state.setdefault(ui_key, st.session_state[real_key])
            if st.session_state[ui_key] not in cat_options:
                st.session_state[ui_key] = CATEGORY_NONE_LABEL

            def _on_new_category_change() -> None:
                sel = st.session_state.get(ui_key, CATEGORY_NONE_LABEL)

                # "Kategorien verwalten…" => Panel öffnen und Auswahl zurücksetzen
                if sel == CAT_MANAGE_LABEL:
                    controller.set_ui_value("show_categories", True)
                    st.session_state[ui_key] = st.session_state.get(real_key, CATEGORY_NONE_LABEL)
                    st.session_state["__request_rerun__"] = True
                    return

                # Normaler Wert => in echten Wert übernehmen
                st.session_state[real_key] = sel

            st.selectbox(
                "Kategorie",
                options=cat_options,
                key=ui_key,  # UI-Key
                label_visibility="collapsed",
                on_change=_on_new_category_change,
            )

            # Rerun außerhalb des Callbacks (Streamlit-konform)
            if st.session_state.pop("__request_rerun__", False):
                st.rerun()

        # ✅ Kategorieverwaltung ÜBER dem "Hinzufügen"-Button
        is_open = controller.get_ui_value("show_categories", False)
        if is_open:
            _render_category_management(controller)

        # Hinzufügen-Button (unterhalb)
        st.button(
            "Hinzufügen",
            icon=ICON_ADD_CIRCLE,
            type="primary",
            on_click=controller.add_task,
            key="add_btn",
            use_container_width=True,
        )


def _render_category_management(controller: TodoController) -> None:
    """Rendert die Kategorieverwaltung."""
    can_add = controller.can_add_category()

    # Neue Kategorie hinzufügen + Close-Icon in derselben Zeile (auf gleicher Höhe)
    col_input, col_btn, col_close = st.columns(
        [0.70, 0.22, 0.08],
        vertical_alignment="bottom",
    )

    with col_input:
        st.text_input(
            "Neue Kategorie",
            key="cat_new_name",
            placeholder="z.B. Uni, Haushalt …",
            disabled=not can_add,
            label_visibility="collapsed",
        )

    with col_btn:
        st.button(
            "Erstellen",
            icon=ICON_ADD_CIRCLE,
            type="primary",
            on_click=controller.add_category,
            key="cat_add_btn",
            use_container_width=True,
            disabled=not can_add,
        )

    with col_close:
        if st.button(
            "\u200b",  # nur Icon
            icon=ICON_CANCEL,
            type="tertiary",
            key="cat_close_btn",
            help="Kategorieverwaltung schließen",
            use_container_width=True,
        ):
            controller.set_ui_value("show_categories", False)
            st.rerun()

    if not can_add:
        st.caption("Maximal 5 Kategorien möglich.")

    # Bestehende Kategorien anzeigen
    current = controller.list_categories()
    if not current:
        st.caption("Noch keine Kategorien vorhanden.")
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
        else:
            for task in tasks:
                _render_task_row(controller, task)


def _render_filter(controller: TodoController) -> None:
    """Rendert die Filter-Segmente."""
    opt_all = "Alle"
    opt_open = "Offen"
    opt_done = "Erledigt"
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