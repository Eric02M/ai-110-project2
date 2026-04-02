from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90)

mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")

# --- Tasks for Mochi ---
mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority="high",
                    reason="Daily exercise keeps Mochi healthy"))
mochi.add_task(Task(title="Brush coat", duration_minutes=15, priority="medium",
                    reason="Reduces shedding"))

# --- Tasks for Luna ---
luna.add_task(Task(title="Clean litter box", duration_minutes=10, priority="high",
                   reason="Hygiene essential"))
luna.add_task(Task(title="Playtime with wand toy", duration_minutes=20, priority="medium",
                   reason="Mental stimulation"))
luna.add_task(Task(title="Administer ear drops", duration_minutes=5, priority="high",
                   reason="Prescribed medication"))

# --- Register pets with owner ---
owner.add_pet(mochi)
owner.add_pet(luna)

# --- Schedule ---
scheduler = Scheduler(owner)
scheduler.build_plan()

print("=" * 50)
print("         TODAY'S SCHEDULE")
print("=" * 50)
print(scheduler.explain_plan())
print("=" * 50)
