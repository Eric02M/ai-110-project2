import streamlit as st
from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Your daily pet care planner — priority-first, conflict-free.")

st.divider()

# ── Owner & Pet Setup ────────────────────────────────────────────────────────

st.subheader("Owner & Pet Info")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Available time today (minutes)", min_value=1, max_value=480, value=90
    )
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "rabbit", "other"])

st.divider()

# ── Task Entry ───────────────────────────────────────────────────────────────

st.subheader("Add Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
with col5:
    due_date = st.date_input("Due date", value=date.today())

if st.button("Add task"):
    st.session_state.tasks.append({
        "title": task_title,
        "duration_minutes": int(duration),
        "priority": priority,
        "frequency": frequency,
        "due_date": due_date,
    })
    st.success(f'Task "{task_title}" added.')

if st.session_state.tasks:
    st.markdown("**Current tasks:**")
    st.table(st.session_state.tasks)

    if st.button("Clear all tasks"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("No tasks yet — add one above.")

st.divider()

# ── Schedule Generation ───────────────────────────────────────────────────────

st.subheader("Build Schedule")

if st.button("Generate schedule", type="primary"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        # Wire session state into domain objects
        owner = Owner(name=owner_name, available_minutes=int(available_minutes))
        pet = Pet(name=pet_name, species=species)
        for t in st.session_state.tasks:
            pet.add_task(Task(
                title=t["title"],
                duration_minutes=t["duration_minutes"],
                priority=t["priority"],
                frequency=t["frequency"],
                due_date=t["due_date"],
            ))
        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        plan = scheduler.build_plan()

        if not plan:
            st.warning(
                "No tasks could be scheduled. "
                "Try increasing available time or reducing task durations."
            )
        else:
            # ── Conflict check ────────────────────────────────────────────
            conflicts = scheduler.detect_conflicts()
            if conflicts:
                for a, b in conflicts:
                    st.warning(
                        f"⚠️ Conflict: **{a.task.title}** "
                        f"({a.start_minute}–{a.end_minute} min) overlaps "
                        f"**{b.task.title}** ({b.start_minute}–{b.end_minute} min)"
                    )
            else:
                st.success("No scheduling conflicts detected.")

            # ── Sorted schedule table ─────────────────────────────────────
            st.markdown("### Schedule (sorted by start time)")
            sorted_plan = scheduler.sort_by_time()

            rows = []
            for st_task in sorted_plan:
                h_s, m_s = divmod(st_task.start_minute, 60)
                h_e, m_e = divmod(st_task.end_minute, 60)
                rows.append({
                    "Start": f"{h_s:02d}:{m_s:02d}",
                    "End": f"{h_e:02d}:{m_e:02d}",
                    "Task": st_task.task.title,
                    "Priority": st_task.task.priority,
                    "Duration (min)": st_task.task.duration_minutes,
                    "Why": st_task.reasoning,
                })
            st.table(rows)

            # ── Summary metrics ───────────────────────────────────────────
            total_scheduled = sum(r["Duration (min)"] for r in rows)
            skipped = len(st.session_state.tasks) - len(plan)

            m1, m2, m3 = st.columns(3)
            m1.metric("Tasks scheduled", len(plan))
            m2.metric("Time used (min)", f"{total_scheduled} / {int(available_minutes)}")
            m3.metric("Tasks skipped", skipped)

            # ── Incomplete tasks filter ───────────────────────────────────
            st.markdown("### Pending (incomplete) tasks")
            incomplete = scheduler.filter_tasks(completed=False)
            if incomplete:
                for item in incomplete:
                    freq_label = (
                        f" · repeats {item.task.frequency}"
                        if item.task.frequency != "once"
                        else ""
                    )
                    st.write(f"- **{item.task.title}** ({item.task.priority} priority{freq_label})")
            else:
                st.success("All scheduled tasks are complete!")
