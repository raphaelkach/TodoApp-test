import streamlit as st
from controller.todo_controller import TodoController
from model.repository import SessionStateTaskRepository
from model.service import TodoService

st.set_page_config(page_title="TODO-App", layout="centered")
st.title("TODO-App")

repo = SessionStateTaskRepository(st.session_state)
service = TodoService(repo)
controller = TodoController(service)

controller.initialize()

with st.form("add_form", clear_on_submit=True):
    title = st.text_input("Neue Aufgabe")
    if st.form_submit_button("Hinzufügen"):
        controller.add(title)

st.divider()

tasks = controller.list()


def on_delete(task_id: int):
    controller.delete(task_id)


st.subheader(f"Aufgaben ({len(tasks)})")

if not tasks:
    st.info("Noch keine Aufgaben.")
else:
    for t in tasks:
        with st.container(border=True):
            col_chk, col_title, col_del = st.columns(
                [0.08, 0.80, 0.12],
                vertical_alignment="center",
            )

            with col_chk:
                st.checkbox("", value=False, disabled=True, key=f"chk_{t.id}")

            with col_title:
                st.markdown(t.title)

            with col_del:
                spacer, btn = st.columns(
                    [0.55, 0.45], vertical_alignment="center")
                with btn:
                    st.button(
                        label="",
                        icon=":material/delete_forever:",
                        type="tertiary",
                        help="Löschen",
                        key=f"del_{t.id}",
                        on_click=on_delete,
                        args=(t.id,),
                        use_container_width=True,
                    )
