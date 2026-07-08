import streamlit as st
from pawpal_system import Owner, Pet, CareTask, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+.

This app is now connected to your backend logic in `pawpal_system.py`.
Use the controls below to add pets, add tasks, and generate a schedule.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name)
if owner_name != owner.name:
    owner.name = owner_name

col_start, col_end = st.columns(2)
with col_start:
    available_start = st.text_input("Available start (HH:MM)", value=owner.available_start)
with col_end:
    available_end = st.text_input("Available end (HH:MM)", value=owner.available_end)

if st.button("Update availability"):
    owner.set_availability(available_start, available_end)
    st.success("Availability updated.")

st.divider()

st.subheader("Pets")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
breed = st.text_input("Breed (optional)", value="")

if st.button("Add pet"):
    existing_names = {pet.name.lower() for pet in owner.get_pets()}
    cleaned_name = pet_name.strip()
    if not cleaned_name:
        st.error("Please provide a pet name.")
    elif cleaned_name.lower() in existing_names:
        st.warning(f"Pet '{cleaned_name}' already exists.")
    else:
        owner.add_pet(Pet(name=cleaned_name, species=species, breed=breed or None))
        st.success(f"Added pet: {cleaned_name}")

if owner.get_pets():
    st.write("Current pets:")
    pet_rows = [
        {"name": pet.name, "species": pet.species, "breed": pet.breed or "-"}
        for pet in owner.get_pets()
    ]
    st.table(pet_rows)
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add tasks directly to a selected pet.")

if owner.get_pets():
    selected_pet_name = st.selectbox(
        "Select pet for this task",
        [pet.name for pet in owner.get_pets()],
    )
    selected_pet = next(p for p in owner.get_pets() if p.name == selected_pet_name)
else:
    selected_pet = None
    st.info("Add at least one pet before adding tasks.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if selected_pet is None:
        st.error("Please add a pet first.")
    elif not task_title.strip():
        st.error("Please provide a task title.")
    else:
        selected_pet.add_task(
            CareTask(name=task_title.strip(), duration=int(duration), priority=priority)
        )
        st.success(f"Added task '{task_title.strip()}' to {selected_pet.name}.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    task_rows = []
    for pet in owner.get_pets():
        for task in pet.get_tasks():
            task_rows.append(
                {
                    "pet": pet.name,
                    "task": task.name,
                    "duration_minutes": task.duration,
                    "priority": task.priority,
                    "completed": task.completed,
                }
            )
    st.table(task_rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a schedule using your `Scheduler` logic layer.")

if st.button("Generate schedule"):
    if not owner.get_pets():
        st.warning("Please add at least one pet.")
    elif not owner.get_all_tasks():
        st.warning("Please add at least one task.")
    else:
        scheduler = Scheduler(owner)
        plans = scheduler.generate_plan()

        st.success("Schedule generated.")
        for plan in plans:
            st.markdown(f"#### {plan.pet.name} ({plan.pet.species})")
            if plan.scheduled_tasks:
                schedule_rows = [
                    {
                        "start": item.start_time,
                        "end": item.end_time,
                        "task": item.task.name,
                        "duration": item.task.duration,
                        "priority": item.task.priority,
                    }
                    for item in plan.scheduled_tasks
                ]
                st.table(schedule_rows)
            else:
                st.info("No tasks scheduled for this pet.")

            if plan.skipped_tasks:
                st.caption("Skipped tasks")
                skipped_rows = [
                    {
                        "task": item.name,
                        "duration": item.duration,
                        "priority": item.priority,
                    }
                    for item in plan.skipped_tasks
                ]
                st.table(skipped_rows)

            with st.expander("Plan explanation"):
                st.text(plan.display_plan())
