"""
View-Schicht für die Todo-App UI-Darstellung.

Einheitliches, schmales Layout:
- Alle Bereiche (Neue Aufgabe, Fortschritt, Aufgabenliste) untereinander
- Schmale max-width für Desktop
- View verwaltet eigenen UI-State
"""

from __future__ import annotations

import streamlit as st

from controller.todo_controller import TodoController
from model.constants import (
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


# UI-Label für "Kategorien verwalten" direkt in der Kategorie-Selectbox
CAT_MANAGE_LABEL = "➕ Kategorien verwalten…"


def get_responsive_css() -> str:
    """
    Gibt das CSS für die App zurück.

    Einheitliches, schmales Layout für alle Bildschirmgrößen.
    Überschreibt Streamlits internes Column-Breaking bei ~640px.
    """
    return """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 30rem;
        margin: 0 auto;
    }
    
    h1 {
        text-align: center;
    }
    
    /* Verhindert Streamlits automatisches Column-Stacking */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
    }
    
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        min-width: 0 !important;
    }
    
    /* Reduziere Abstand zwischen Titel und Meta-Informationen */
    .element-container:has(+ .element-container p[style*="font-size: 0.875rem"]) {
        margin-bottom: -1rem !important;
    }
    
    /* Alternative: Reduziere Abstand für alle Paragraphen gefolgt von Captions */
    div[data-testid="stMarkdownContainer"] + div[data-testid="stCaptionContainer"] {
        margin-top: -1rem !important;
    }
    
    /* Reduziere Abstand bei st.caption direkt */
    [data-testid="stCaptionContainer"] {
        margin-top: -0.75rem !important;
        padding-top: 0 !important;
    }
    
    /* Angleichung von Kategorie-Text und Input-Feld */
    .category-name-text {
        padding: 0.4rem 0.82rem;
        line-height: 1.6;
        min-height: 2.5rem;
        display: flex;
        align-items: center;
    }
    </style>
    """


def render_app(controller: TodoController) -> None:
    """Hauptfunktion zum Rendern der gesamten App."""
    # CSS einbinden
    st.markdown(get_responsive_css(), unsafe_allow_html=True)

    st.title("Todo-App")

    # Alle Bereiche untereinander
    _render_add_form(controller)
    _render_kpi_panel(controller)
    _render_task_list(controller)


def _render_kpi_panel(controller: TodoController) -> None:
    """Rendert KPI und Fortschritt (Erledigt-Progress) für Aufgaben."""
    all_count, open_count, done_count = controller.get_task_counts()
    percent_done = int(round((done_count / all_count) * 100)) if all_count else 0

    with st.container(border=True):
        st.write("**Fortschritt**")

        # Custom HTML für Metriken
        st.markdown(
            f"""
        <div style="display: flex; gap: 0.5rem; justify-content: space-between; margin-bottom: 0.5rem;">
            <div style="text-align: center; flex: 1;">
                <div style="font-size: 0.85rem; opacity: 0.6;">Gesamt</div>
                <div style="font-size: 1.8rem; font-weight: 600;">{all_count}</div>
            </div>
            <div style="text-align: center; flex: 1;">
                <div style="font-size: 0.85rem; opacity: 0.6;">Offen</div>
                <div style="font-size: 1.8rem; font-weight: 600;">{open_count}</div>
            </div>
            <div style="text-align: center; flex: 1;">
                <div style="font-size: 0.85rem; opacity: 0.6;">Erledigt</div>
                <div style="font-size: 1.8rem; font-weight: 600;">{done_count}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.progress(percent_done)
        st.caption(f"Erledigt: {done_count}/{all_count} ({percent_done}%)")


def _render_add_form(controller: TodoController) -> None:
    """Rendert das Formular zum Hinzufügen neuer Aufgaben."""
    # Initialisiere Session State für neue Aufgaben
    if "new_priority" not in st.session_state:
        st.session_state.new_priority = None
    
    with st.container(border=True):
        st.write("**Neue Aufgabe**")

        # Zeile 1: Titel + Deadline
        col_title, col_dead = st.columns([0.65, 0.35], gap="small")

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

        # Zeile 2: Priorität + Kategorie
        col_prio, col_cat = st.columns([0.50, 0.50], gap="small")

        with col_prio:
            # Verwende Platzhalter-String statt None
            prio_placeholder = "Priorität auswählen"
            prio_options = [prio_placeholder] + PRIORITY_OPTIONS
            
            # Initialisiere mit Platzhalter, wenn None
            if st.session_state.new_priority is None:
                prio_value = prio_placeholder
            else:
                prio_value = st.session_state.new_priority
            
            # Temporärer Key für die UI
            if "new_priority_ui" not in st.session_state:
                st.session_state.new_priority_ui = prio_value
            
            def _on_priority_change():
                selected = st.session_state.new_priority_ui
                if selected == prio_placeholder:
                    st.session_state.new_priority = None
                else:
                    st.session_state.new_priority = selected
            
            st.selectbox(
                "Priorität",
                options=prio_options,
                key="new_priority_ui",
                on_change=_on_priority_change,
                label_visibility="collapsed",
            )

        with col_cat:
            categories = controller.list_categories()
            
            # Verwende String-Platzhalter statt None
            cat_placeholder = "Kategorie auswählen"
            cat_options = [cat_placeholder] + categories + ["__manage__"]

            # Separater UI-Key für die Selectbox
            ui_key = "new_category_ui"
            real_key = "new_category"
            
            # Initialisiere Keys
            if real_key not in st.session_state:
                st.session_state[real_key] = None
            
            # Validiere: Wenn gespeicherte Kategorie nicht mehr existiert, auf None setzen
            if st.session_state[real_key] is not None:
                if st.session_state[real_key] not in categories:
                    st.session_state[real_key] = None
            
            # Konvertiere None zu Platzhalter für UI
            if st.session_state[real_key] is None:
                display_value = cat_placeholder
            else:
                display_value = st.session_state[real_key]
            
            if ui_key not in st.session_state:
                st.session_state[ui_key] = display_value

            def _on_category_change():
                selected = st.session_state.get(ui_key)
                if selected == "__manage__":
                    st.session_state.show_category_dialog = True
                    # Setze UI-Key zurück auf den Display-Wert
                    if st.session_state[real_key] is None:
                        st.session_state[ui_key] = cat_placeholder
                    else:
                        st.session_state[ui_key] = st.session_state[real_key]
                elif selected == cat_placeholder:
                    st.session_state[real_key] = None
                else:
                    st.session_state[real_key] = selected
            
            st.selectbox(
                "Kategorie",
                options=cat_options,
                format_func=lambda x: CAT_MANAGE_LABEL if x == "__manage__" else x,
                key=ui_key,
                on_change=_on_category_change,
                label_visibility="collapsed",
            )

        # ✅ View verwaltet Dialog-State selbst
        if st.session_state.get("show_category_dialog", False):
            _render_category_management(controller)

        # ✅ Button ruft Controller mit Parametern
        def _on_add_click():
            title = st.session_state.get("new_title", "").strip()
            if not title:
                return

            success = controller.add_task(
                title=title,
                due_date=st.session_state.get("add_due_date"),
                category=st.session_state.get("new_category"),  # Real key
                priority=st.session_state.get("new_priority"),
            )

            # ✅ View resettet ihre eigenen Felder
            if success:
                st.session_state.new_title = ""
                st.session_state.add_due_date = None
                st.session_state.new_priority = None
                st.session_state.new_priority_ui = "Priorität auswählen"
                st.session_state.new_category = None
                st.session_state.new_category_ui = "Kategorie auswählen"

        st.button(
            "Hinzufügen",
            icon=ICON_ADD_CIRCLE,
            type="primary",
            on_click=_on_add_click,
            key="add_btn",
            use_container_width=True,
        )


def _format_category_option(value):
    """Formatiert Kategorie-Optionen für Selectbox."""
    if value is None:
        return "Kategorie auswählen"
    elif value == "__manage__":
        return CAT_MANAGE_LABEL
    return value


def _render_category_management(controller: TodoController) -> None:
    """Rendert die Kategorieverwaltung."""
    can_add = controller.can_add_category()

    # Layout: Input + Button + Close
    col_input, col_btn, col_close = st.columns([0.55, 0.35, 0.10], gap="small")

    with col_input:
        st.text_input(
            "Neue Kategorie",
            key="cat_new_name",
            placeholder="z.B. Uni, Haushalt …",
            disabled=not can_add,
            label_visibility="collapsed",
        )

    with col_btn:

        def _on_add_category():
            name = st.session_state.get("cat_new_name", "").strip()
            if name and controller.add_category(name):
                st.session_state.cat_new_name = ""

        st.button(
            "Erstellen",
            icon=ICON_ADD_CIRCLE,
            type="primary",
            on_click=_on_add_category,
            key="cat_add_btn",
            use_container_width=True,
            disabled=not can_add,
        )

    with col_close:

        def _close_dialog():
            st.session_state.show_category_dialog = False
            st.rerun()

        st.button(
            "\u200b",
            icon=ICON_CANCEL,
            type="tertiary",
            key="cat_close_btn",
            help="Kategorieverwaltung schließen",
            on_click=_close_dialog,
            use_container_width=True,
        )

    if not can_add:
        st.caption("Maximal 5 Kategorien möglich.")

    current = controller.list_categories()
    if not current:
        st.caption("Noch keine Kategorien vorhanden.")
        return

    # ✅ View verwaltet Rename-State selbst
    rename_target = st.session_state.get("cat_rename_target")

    for i, cat in enumerate(current):
        if rename_target == cat:
            _render_category_edit_row(controller, cat, i)
        else:
            _render_category_view_row(controller, cat, i)


def _render_category_edit_row(
    controller: TodoController, cat: str, index: int
) -> None:
    """Rendert eine Kategorie-Zeile im Bearbeitungsmodus."""
    col_name, col_btn1, col_btn2, _col_spacer = st.columns(
        [0.55, 0.175, 0.175, 0.10], gap="small"
    )

    with col_name:
        # ✅ Edit-Value in Session State
        if "cat_rename_value" not in st.session_state:
            st.session_state.cat_rename_value = cat

        st.text_input(
            "Umbenennen", key="cat_rename_value", label_visibility="collapsed"
        )

    with col_btn1:

        def _on_save():
            new_name = st.session_state.get("cat_rename_value", "").strip()
            if new_name and controller.rename_category(cat, new_name):
                st.session_state.cat_rename_target = None
                st.session_state.cat_rename_value = ""

        st.button(
            "\u200b",
            icon=ICON_SAVE,
            type="tertiary",
            key=f"cat_save_{index}",
            on_click=_on_save,
            help="Speichern",
            use_container_width=True,
        )

    with col_btn2:

        def _on_cancel():
            st.session_state.cat_rename_target = None
            st.session_state.cat_rename_value = ""

        st.button(
            "\u200b",
            icon=ICON_CANCEL,
            type="tertiary",
            key=f"cat_cancel_{index}",
            on_click=_on_cancel,
            help="Abbrechen",
            use_container_width=True,
        )


def _render_category_view_row(
    controller: TodoController, cat: str, index: int
) -> None:
    """Rendert eine Kategorie-Zeile im Ansichtsmodus."""
    col_name, col_btn1, col_btn2, _col_spacer = st.columns(
        [0.55, 0.175, 0.175, 0.10], gap="small"
    )

    with col_name:
        st.markdown(
            f'<div class="category-name-text">{cat}</div>', unsafe_allow_html=True
        )

    with col_btn1:

        def _on_edit():
            st.session_state.cat_rename_target = cat
            st.session_state.cat_rename_value = cat

        st.button(
            "\u200b",
            icon=ICON_EDIT,
            type="tertiary",
            key=f"cat_edit_{index}",
            on_click=_on_edit,
            help="Umbenennen",
            use_container_width=True,
        )

    with col_btn2:
        st.button(
            "\u200b",
            icon=ICON_DELETE,
            type="tertiary",
            key=f"cat_del_{index}",
            on_click=lambda: controller.delete_category(cat),
            help="Löschen",
            use_container_width=True,
        )


def _render_task_list(controller: TodoController) -> None:
    """Rendert die Aufgabenliste mit Filter."""
    with st.container(border=True):
        st.write("**Aufgabenliste**")

        _render_filter(controller)

        # ✅ View holt gefilterte Tasks mit Parameter
        filter_value = st.session_state.get("task_filter", FILTER_ALL)
        tasks = controller.get_filtered_tasks(filter_value)

        if not tasks:
            st.info("Noch keine Aufgaben.")
        else:
            for task in tasks:
                _render_task_row(controller, task)


def _render_filter(controller: TodoController) -> None:
    """Rendert die Filter-Segmente."""
    options = [FILTER_ALL, FILTER_OPEN, FILTER_DONE]

    # Default-Filter setzen, falls noch nicht vorhanden
    if "task_filter" not in st.session_state:
        st.session_state.task_filter = FILTER_ALL

    # Segmented Control oder Radio (fallback)
    if hasattr(st, "segmented_control"):
        st.segmented_control(
            "Filter",
            options=options,
            label_visibility="collapsed",
            key="task_filter",
        )
    else:
        st.radio(
            "Filter",
            options,
            horizontal=True,
            label_visibility="collapsed",
            key="task_filter",
        )


def _render_task_row(controller: TodoController, task) -> None:
    """Rendert eine einzelne Task-Zeile."""
    # ✅ View verwaltet Edit-State selbst
    editing_id = st.session_state.get("editing_task_id")
    is_editing = editing_id == task.id

    with st.container(border=True):
        if is_editing:
            # Bearbeitungsmodus
            col_chk, col_main = st.columns(
                [0.06, 0.94], gap="small", vertical_alignment="center"
            )

            with col_chk:
                st.checkbox(
                    "\u200b",
                    value=task.done,
                    key=f"done_{task.id}",
                    label_visibility="collapsed",
                    on_change=lambda: controller.toggle_task_done(
                        task.id, st.session_state[f"done_{task.id}"]
                    ),
                    help="Als erledigt markieren",
                )

            with col_main:
                _render_task_edit_content(controller, task)
        else:
            # Ansichtsmodus
            col_chk, col_main, col_buttons = st.columns(
                [0.06, 0.78, 0.16], gap="small", vertical_alignment="center"
            )

            with col_chk:
                st.checkbox(
                    "\u200b",
                    value=task.done,
                    key=f"done_{task.id}",
                    label_visibility="collapsed",
                    on_change=lambda: controller.toggle_task_done(
                        task.id, st.session_state[f"done_{task.id}"]
                    ),
                    help="Als erledigt markieren",
                )

            with col_main:
                _render_task_view_content(task)

            with col_buttons:
                _render_task_view_buttons(controller, task)


def _render_task_view_content(task) -> None:
    """Rendert den Inhalt einer Task-Zeile im Ansichtsmodus."""
    # Titel in erster Zeile
    if task.done:
        st.markdown(f"~~{task.title}~~")
    else:
        st.write(task.title)

    # Meta-Informationen in zweiter Zeile
    meta_parts = []

    if task.due_date:
        meta_parts.append(task.due_date.strftime("%d.%m.%Y"))

    priority = getattr(task, "priority", None)
    if priority and priority in PRIO_ICONS:
        icon = PRIO_ICONS[priority]
        meta_parts.append(f"{icon} {priority}")

    if task.category:
        meta_parts.append(task.category)

    if meta_parts:
        separator = " &nbsp;&nbsp;·&nbsp;&nbsp; "
        meta_text = separator.join(meta_parts)
        st.caption(meta_text)


def _render_task_edit_content(controller: TodoController, task) -> None:
    """Rendert den Inhalt einer Task-Zeile im Bearbeitungsmodus."""
    # ✅ View speichert Edit-Daten in eigenen Keys beim ersten Mal
    if f"edit_title_{task.id}" not in st.session_state:
        st.session_state[f"edit_title_{task.id}"] = task.title
        st.session_state[f"edit_due_{task.id}"] = task.due_date
        st.session_state[f"edit_priority_{task.id}"] = task.priority
        st.session_state[f"edit_category_{task.id}"] = task.category
        
        # Initialisiere auch die UI-Keys
        prio_placeholder = "Priorität auswählen"
        cat_placeholder = "Kategorie auswählen"
        
        if task.priority is None:
            st.session_state[f"edit_priority_ui_{task.id}"] = prio_placeholder
        else:
            st.session_state[f"edit_priority_ui_{task.id}"] = task.priority
            
        if task.category is None:
            st.session_state[f"edit_category_ui_{task.id}"] = cat_placeholder
        else:
            st.session_state[f"edit_category_ui_{task.id}"] = task.category
    
    # Validiere Kategorie: Wenn gelöscht, auf None setzen
    categories = controller.list_categories()
    current_cat = st.session_state.get(f"edit_category_{task.id}")
    if current_cat is not None and current_cat not in categories:
        st.session_state[f"edit_category_{task.id}"] = None
        st.session_state[f"edit_category_ui_{task.id}"] = "Kategorie auswählen"

    # Zeile 1: Titel + Deadline + Abbrechen
    col_title, col_dead, col_cancel = st.columns([0.45, 0.47, 0.08], gap="small")

    with col_title:
        st.text_input(
            "Titel",
            key=f"edit_title_{task.id}",
            label_visibility="collapsed",
        )

    with col_dead:
        st.date_input(
            "Deadline",
            key=f"edit_due_{task.id}",
            value=None,
            label_visibility="collapsed",
            format="DD.MM.YYYY",
        )

    with col_cancel:

        def _on_cancel():
            # ✅ View löscht ihre Edit-Keys
            st.session_state.pop(f"edit_title_{task.id}", None)
            st.session_state.pop(f"edit_due_{task.id}", None)
            st.session_state.pop(f"edit_priority_{task.id}", None)
            st.session_state.pop(f"edit_priority_ui_{task.id}", None)
            st.session_state.pop(f"edit_category_{task.id}", None)
            st.session_state.pop(f"edit_category_ui_{task.id}", None)
            st.session_state.editing_task_id = None

        st.button(
            "\u200b",
            icon=ICON_CANCEL,
            type="tertiary",
            help="Abbrechen",
            key=f"cancel_{task.id}",
            on_click=_on_cancel,
            use_container_width=True,
        )

    # Zeile 2: Priorität + Kategorie + Speichern
    col_prio, col_cat, col_save = st.columns([0.45, 0.47, 0.08], gap="small")

    with col_prio:
        # Verwende Platzhalter-String statt None
        prio_placeholder = "Priorität auswählen"
        prio_options = [prio_placeholder] + PRIORITY_OPTIONS
        
        # Konvertiere aktuellen Wert
        current_prio = st.session_state.get(f"edit_priority_{task.id}")
        if current_prio is None or current_prio not in PRIORITY_OPTIONS:
            display_value = prio_placeholder
        else:
            display_value = current_prio
        
        # Temporärer UI-Key
        ui_prio_key = f"edit_priority_ui_{task.id}"
        if ui_prio_key not in st.session_state:
            st.session_state[ui_prio_key] = display_value
        
        def _on_edit_priority_change():
            selected = st.session_state[ui_prio_key]
            if selected == prio_placeholder:
                st.session_state[f"edit_priority_{task.id}"] = None
            else:
                st.session_state[f"edit_priority_{task.id}"] = selected
        
        st.selectbox(
            "Priorität",
            options=prio_options,
            key=ui_prio_key,
            on_change=_on_edit_priority_change,
            label_visibility="collapsed",
        )

    with col_cat:
        # Verwende Platzhalter-String statt None
        cat_placeholder = "Kategorie auswählen"
        cat_options = [cat_placeholder] + categories
        
        # Konvertiere aktuellen Wert
        current_cat = st.session_state.get(f"edit_category_{task.id}")
        if current_cat is None or current_cat not in categories:
            display_cat_value = cat_placeholder
        else:
            display_cat_value = current_cat
        
        # Temporärer UI-Key
        ui_cat_key = f"edit_category_ui_{task.id}"
        if ui_cat_key not in st.session_state:
            st.session_state[ui_cat_key] = display_cat_value
        
        def _on_edit_category_change():
            selected = st.session_state[ui_cat_key]
            if selected == cat_placeholder:
                st.session_state[f"edit_category_{task.id}"] = None
            else:
                st.session_state[f"edit_category_{task.id}"] = selected
        
        st.selectbox(
            "Kategorie",
            options=cat_options,
            key=ui_cat_key,
            on_change=_on_edit_category_change,
            label_visibility="collapsed",
            disabled=len(categories) == 0,
        )

    with col_save:

        def _on_save():
            # ✅ View sammelt Daten und ruft Controller
            title = st.session_state.get(f"edit_title_{task.id}", "").strip()
            if not title:
                return

            success = controller.update_task(
                task_id=task.id,
                title=title,
                due_date=st.session_state.get(f"edit_due_{task.id}"),
                priority=st.session_state.get(f"edit_priority_{task.id}"),
                category=st.session_state.get(f"edit_category_{task.id}"),
            )

            if success:
                # ✅ View löscht ihre Edit-Keys
                st.session_state.pop(f"edit_title_{task.id}", None)
                st.session_state.pop(f"edit_due_{task.id}", None)
                st.session_state.pop(f"edit_priority_{task.id}", None)
                st.session_state.pop(f"edit_priority_ui_{task.id}", None)
                st.session_state.pop(f"edit_category_{task.id}", None)
                st.session_state.pop(f"edit_category_ui_{task.id}", None)
                st.session_state.editing_task_id = None

        st.button(
            "\u200b",
            icon=ICON_SAVE,
            type="tertiary",
            help="Speichern",
            key=f"save_{task.id}",
            on_click=_on_save,
            use_container_width=True,
        )


def _render_task_view_buttons(controller: TodoController, task) -> None:
    """Rendert die Buttons im Ansichtsmodus."""
    btn1, btn2 = st.columns(2, gap="small")

    with btn1:

        def _on_edit():
            # ✅ View setzt Edit-State
            st.session_state.editing_task_id = task.id

        st.button(
            "\u200b",
            icon=ICON_EDIT,
            type="tertiary",
            help="Bearbeiten",
            key=f"edit_{task.id}",
            on_click=_on_edit,
            use_container_width=True,
        )

    with btn2:
        st.button(
            "\u200b",
            icon=ICON_DELETE,
            type="tertiary",
            help="Löschen",
            key=f"del_{task.id}",
            on_click=lambda: controller.delete_task(task.id),
            use_container_width=True,
        )