from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90)

mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")

# --- Tasks for Mochi ---
mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority="high",
                    reason="Daily exercise keeps Mochi healthy"))

luna.add_task(Task(title="Playtime with wand toy", duration_minutes=20, priority="medium",
                   reason="Mental stimulation"))
luna.add_task(Task(title="Administer ear drops", duration_minutes=5, priority="high",
                   reason="Prescribed medication"))
luna.add_task(Task(title="Clean litter box", duration_minutes=10, priority="high",
                   reason="Hygiene essential"))

# Register pets
owner.add_pet(mochi)
owner.add_pet(luna)

# --- Schedule ---
scheduler = Scheduler(owner)
scheduler.build_plan()

print("=" * 50)
print("         TODAY'S SCHEDULE")
print("=" * 50)
print(scheduler.explain_plan())

# --- Sort by time (HH:MM) ---
print("=" * 50)
print("     SORTED BY START TIME (HH:MM)")
print("=" * 50)
for i, st in enumerate(scheduler.sort_by_time(), 1):
    h_s, m_s = divmod(st.start_minute, 60)
    print(f"{i}. [{h_s:02d}:{m_s:02d}]  {st.task.title}  ({st.task.priority} priority)")

# --- Filter: incomplete tasks only ---
print("=" * 50)
print("     FILTER: INCOMPLETE TASKS")
print("=" * 50)
incomplete = scheduler.filter_tasks(completed=False)
for st in incomplete:
    print(f"  - {st.task.title} [{st.task.pet.name if st.task.pet else 'no pet'}]")

# --- Filter: Mochi's tasks only ---
print("=" * 50)
print("     FILTER: MOCHI'S TASKS")
print("=" * 50)
mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
for st in mochi_tasks:
    print(f"  - {st.task.title} ({st.task.duration_minutes} min)")

# --- Filter: Luna's tasks only ---
print("=" * 50)
print("     FILTER: LUNA'S TASKS")
print("=" * 50)
luna_tasks = scheduler.filter_tasks(pet_name="Luna")
for st in luna_tasks:
    print(f"  - {st.task.title} ({st.task.duration_minutes} min)")

print("=" * 50)



