from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler, ScheduledTask


# --- Task Addition ---

# Test: adding a task to a pet stores it in pet.tasks
# Expected: task appears in pet.tasks list
def test_add_task_to_pet():
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Morning walk", duration_minutes=30, priority="high")
    pet.add_task(task)
    assert task in pet.tasks

# Test: add_task links the task back to the pet via task.pet
# Expected: task.pet is the same pet object it was added to
def test_add_task_sets_pet_reference():
    pet = Pet(name="Luna", species="cat")
    task = Task(title="Playtime", duration_minutes=15, priority="medium")
    pet.add_task(task)
    assert task.pet is pet

# Test: adding multiple tasks to one pet stores all of them
# Expected: pet.tasks has length 2
def test_add_multiple_tasks_to_pet():
    pet = Pet(name="Mochi", species="dog")
    t1 = Task(title="Walk", duration_minutes=20, priority="high")
    t2 = Task(title="Feed", duration_minutes=5, priority="medium")
    pet.add_task(t1)
    pet.add_task(t2)
    assert len(pet.tasks) == 2

# Test: owner.get_all_tasks() collects pending tasks from all pets
# Expected: 2 tasks total (1 from Mochi, 1 from Luna)
def test_owner_get_all_tasks_across_pets():
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    mochi.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    luna.add_task(Task(title="Litter box", duration_minutes=10, priority="high"))
    owner.add_pet(mochi)
    owner.add_pet(luna)
    assert len(owner.get_all_tasks()) == 2


# --- Task Completion ---

# Test: mark_complete() sets task.completed to True
# Expected: task.completed == True
def test_mark_task_complete():
    task = Task(title="Feed", duration_minutes=5, priority="low")
    task.mark_complete()
    assert task.completed is True

# Test: a completed task is excluded from pet.pending_tasks()
# Expected: t2 (completed) not in pending, t1 (incomplete) still in pending
def test_completed_task_excluded_from_pending():
    pet = Pet(name="Mochi", species="dog")
    t1 = Task(title="Walk", duration_minutes=20, priority="high")
    t2 = Task(title="Feed", duration_minutes=5, priority="low")
    pet.add_task(t1)
    pet.add_task(t2)
    t2.mark_complete()
    assert t2 not in pet.pending_tasks()
    assert t1 in pet.pending_tasks()

# Test: a completed task is not included in the scheduled plan
# Expected: "Feed" not in scheduled titles, "Walk" is scheduled
def test_completed_task_not_scheduled():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    t1 = Task(title="Walk", duration_minutes=20, priority="high")
    t2 = Task(title="Feed", duration_minutes=5, priority="low")
    pet.add_task(t1)
    pet.add_task(t2)
    t2.mark_complete()
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    plan = scheduler.build_plan()
    titles = [st.task.title for st in plan]
    assert "Feed" not in titles
    assert "Walk" in titles

# Test: a new task is not completed by default
# Expected: task.completed == False
def test_task_not_complete_by_default():
    task = Task(title="Groom", duration_minutes=10, priority="medium")
    assert task.completed is False


# --- Priority Sorting ---

# Test: high priority task is scheduled before medium priority task
# Expected: "Meds" (high) appears before "Playtime" (medium) in plan
def test_high_priority_scheduled_before_medium():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task(title="Playtime", duration_minutes=20, priority="medium"))
    pet.add_task(Task(title="Meds", duration_minutes=5, priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    plan = scheduler.build_plan()
    titles = [st.task.title for st in plan]
    assert titles.index("Meds") < titles.index("Playtime")

# Test: when priorities are equal, shorter task is scheduled first
# Expected: "Quick feed" (5 min) before "Long groom" (30 min), both medium
def test_same_priority_shorter_task_first():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Long groom", duration_minutes=30, priority="medium"))
    pet.add_task(Task(title="Quick feed", duration_minutes=5, priority="medium"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    plan = scheduler.build_plan()
    titles = [st.task.title for st in plan]
    assert titles.index("Quick feed") < titles.index("Long groom")

# Test: get_priority_score returns correct values for all priority levels
# Expected: high=3, medium=2, low=1, unknown=0
def test_priority_score_values():
    assert Task(title="A", duration_minutes=5, priority="high").get_priority_score() == 3
    assert Task(title="B", duration_minutes=5, priority="medium").get_priority_score() == 2
    assert Task(title="C", duration_minutes=5, priority="low").get_priority_score() == 1
    assert Task(title="D", duration_minutes=5, priority="urgent").get_priority_score() == 0


# --- Time Budget Edge Cases ---

# Test: a task that exactly fills the available time is scheduled
# Expected: 1 task in plan, time_used == time_budget
def test_task_exactly_fills_budget():
    owner = Owner(name="Jordan", available_minutes=30)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, priority="high"))
    owner.add_pet(pet)
    plan = Scheduler(owner).build_plan()
    assert len(plan) == 1
    assert plan[0].task.title == "Walk"

# Test: a task 1 minute over the budget is not scheduled
# Expected: empty plan
def test_task_one_minute_over_budget_not_scheduled():
    owner = Owner(name="Jordan", available_minutes=29)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, priority="high"))
    owner.add_pet(pet)
    plan = Scheduler(owner).build_plan()
    assert len(plan) == 0

# Test: available_minutes=0 produces an empty plan without crashing
# Expected: empty plan
def test_zero_available_minutes():
    owner = Owner(name="Jordan", available_minutes=0)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=10, priority="high"))
    owner.add_pet(pet)
    plan = Scheduler(owner).build_plan()
    assert plan == []

# Test: owner with no pets produces an empty plan
# Expected: empty plan
def test_owner_with_no_pets():
    owner = Owner(name="Jordan", available_minutes=60)
    plan = Scheduler(owner).build_plan()
    assert plan == []

# Test: pet with no tasks produces an empty plan
# Expected: empty plan
def test_pet_with_no_tasks():
    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(Pet(name="Mochi", species="dog"))
    plan = Scheduler(owner).build_plan()
    assert plan == []

# Test: start_minute and end_minute are set correctly for back-to-back tasks
# Expected: first task 0–5, second task 5–25
def test_scheduled_task_time_slots_are_correct():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task(title="Meds", duration_minutes=5, priority="high"))
    pet.add_task(Task(title="Playtime", duration_minutes=20, priority="medium"))
    owner.add_pet(pet)
    plan = Scheduler(owner).build_plan()
    assert plan[0].start_minute == 0
    assert plan[0].end_minute == 5
    assert plan[1].start_minute == 5
    assert plan[1].end_minute == 25


# --- Recurring Tasks ---

# Test: frequency="once" → next_occurrence() returns None
# Expected: None (no follow-up task created)
def test_once_task_has_no_next_occurrence():
    task = Task(title="Vet visit", duration_minutes=60, priority="high", frequency="once")
    assert task.next_occurrence() is None

# Test: frequency="daily" → next due date is due_date + 1 day
# Expected: next_task.due_date == original due_date + timedelta(days=1)
def test_daily_task_next_occurrence_is_tomorrow():
    today = date(2026, 4, 4)
    task = Task(title="Walk", duration_minutes=30, priority="high",
                frequency="daily", due_date=today)
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)

# Test: frequency="weekly" → next due date is due_date + 7 days
# Expected: next_task.due_date == original due_date + timedelta(weeks=1)
def test_weekly_task_next_occurrence_is_seven_days_later():
    today = date(2026, 4, 4)
    task = Task(title="Bath", duration_minutes=20, priority="medium",
                frequency="weekly", due_date=today)
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)

# Test: next_occurrence() with no due_date falls back to date.today()
# Expected: next_task.due_date == date.today() + timedelta(days=1)
def test_daily_task_no_due_date_falls_back_to_today():
    task = Task(title="Walk", duration_minutes=30, priority="high", frequency="daily")
    next_task = task.next_occurrence()
    assert next_task.due_date == date.today() + timedelta(days=1)

# Test: next occurrence copies all task fields (title, duration, priority, frequency)
# Expected: all fields match original except completed=False and updated due_date
def test_next_occurrence_copies_task_fields():
    today = date(2026, 4, 4)
    task = Task(title="Walk", duration_minutes=30, priority="high",
                reason="exercise", frequency="daily", due_date=today)
    next_task = task.next_occurrence()
    assert next_task.title == "Walk"
    assert next_task.duration_minutes == 30
    assert next_task.priority == "high"
    assert next_task.reason == "exercise"
    assert next_task.frequency == "daily"
    assert next_task.completed is False

# Test: mark_task_complete marks original done and adds next task to pet
# Expected: original.completed=True, pet has 2 tasks, new task has tomorrow's date
def test_scheduler_mark_task_complete_adds_next_to_pet():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    today = date(2026, 4, 4)
    task = Task(title="Walk", duration_minutes=30, priority="high",
                frequency="daily", due_date=today)
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task)
    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task in pet.tasks

# Test: mark_task_complete on a "once" task returns None and adds nothing to pet
# Expected: task.completed=True, pet still has only 1 task, return value is None
def test_scheduler_mark_task_complete_once_returns_none():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Luna", species="cat")
    task = Task(title="Vet visit", duration_minutes=60, priority="high", frequency="once")
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    result = scheduler.mark_task_complete(task)
    assert result is None
    assert task.completed is True
    assert len(pet.tasks) == 1

# Test: mark_task_complete on a task with no pet does not crash
# Expected: task.completed=True, next task created but not linked to any pet
def test_mark_task_complete_no_pet_does_not_crash():
    owner = Owner(name="Jordan", available_minutes=60)
    scheduler = Scheduler(owner)
    task = Task(title="Walk", duration_minutes=30, priority="high", frequency="daily",
                due_date=date(2026, 4, 4))
    result = scheduler.mark_task_complete(task)
    assert task.completed is True
    assert result is not None
    assert result.pet is None


# --- Filter and Sort ---

# Test: filter_tasks(completed=False) returns only incomplete tasks
# Expected: only the uncompleted task appears
def test_filter_incomplete_tasks():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    t1 = Task(title="Walk", duration_minutes=20, priority="high")
    t2 = Task(title="Feed", duration_minutes=5, priority="low")
    pet.add_task(t1)
    pet.add_task(t2)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.build_plan()
    t1.mark_complete()
    incomplete = scheduler.filter_tasks(completed=False)
    titles = [st.task.title for st in incomplete]
    assert "Walk" not in titles
    assert "Feed" in titles

# Test: filter_tasks(pet_name="Mochi") returns only Mochi's tasks
# Expected: only Walk in results, not Luna's Playtime
def test_filter_by_pet_name():
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    mochi.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    luna.add_task(Task(title="Playtime", duration_minutes=15, priority="medium"))
    owner.add_pet(mochi)
    owner.add_pet(luna)
    scheduler = Scheduler(owner)
    scheduler.build_plan()
    results = scheduler.filter_tasks(pet_name="Mochi")
    titles = [st.task.title for st in results]
    assert "Walk" in titles
    assert "Playtime" not in titles

# Test: filter_tasks with a pet name that has no scheduled tasks returns []
# Expected: empty list, no crash
def test_filter_by_nonexistent_pet_returns_empty():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.build_plan()
    results = scheduler.filter_tasks(pet_name="Ghost")
    assert results == []

# Test: sort_by_time returns tasks ordered by start_minute ascending
# Expected: tasks sorted 00:00 → 00:05 → 00:25
def test_sort_by_time_returns_ascending_order():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Luna", species="cat")
    pet.add_task(Task(title="Meds", duration_minutes=5, priority="high"))
    pet.add_task(Task(title="Playtime", duration_minutes=20, priority="medium"))
    pet.add_task(Task(title="Brush", duration_minutes=10, priority="low"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.build_plan()
    sorted_plan = scheduler.sort_by_time()
    start_times = [st.start_minute for st in sorted_plan]
    assert start_times == sorted(start_times)


# --- explain_plan ---

# Test: explain_plan before build_plan returns a helpful message
# Expected: string contains "No tasks scheduled"
def test_explain_plan_before_build_returns_message():
    owner = Owner(name="Jordan", available_minutes=60)
    scheduler = Scheduler(owner)
    output = scheduler.explain_plan()
    assert "No tasks scheduled" in output

# Test: explain_plan after build_plan includes owner name and total time
# Expected: output contains "Jordan" and "Total time"
def test_explain_plan_includes_owner_and_total():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.build_plan()
    output = scheduler.explain_plan()
    assert "Jordan" in output
    assert "Total time" in output


# --- Conflict Detection ---

# Test: a normally built plan has no conflicts (sequential slots never overlap)
# Expected: detect_conflicts() returns []
def test_no_conflicts_in_normal_plan():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    pet.add_task(Task(title="Feed", duration_minutes=10, priority="medium"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    scheduler.build_plan()
    assert scheduler.detect_conflicts() == []

# Test: two tasks with fully overlapping slots are flagged as a conflict
# Walk runs 0–30, Meds runs 0–5 — Meds starts inside Walk's window
# Expected: detect_conflicts() returns 1 conflicting pair
def test_fully_overlapping_tasks_detected():
    owner = Owner(name="Jordan", available_minutes=60)
    scheduler = Scheduler(owner)
    task_a = Task(title="Walk", duration_minutes=30, priority="high")
    task_b = Task(title="Meds", duration_minutes=5, priority="high")
    scheduler.scheduled_tasks = [
        ScheduledTask(task=task_a, start_minute=0, end_minute=30),
        ScheduledTask(task=task_b, start_minute=0, end_minute=5),
    ]
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    titles = {conflicts[0][0].task.title, conflicts[0][1].task.title}
    assert titles == {"Walk", "Meds"}

# Test: two tasks with partially overlapping slots are flagged
# Walk runs 0–30, Feed runs 20–30 — Feed starts before Walk ends
# Expected: detect_conflicts() returns 1 conflicting pair
def test_partially_overlapping_tasks_detected():
    owner = Owner(name="Jordan", available_minutes=60)
    scheduler = Scheduler(owner)
    task_a = Task(title="Walk", duration_minutes=30, priority="high")
    task_b = Task(title="Feed", duration_minutes=10, priority="medium")
    scheduler.scheduled_tasks = [
        ScheduledTask(task=task_a, start_minute=0, end_minute=30),
        ScheduledTask(task=task_b, start_minute=20, end_minute=30),
    ]
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1

# Test: tasks that share only an endpoint do not count as a conflict
# Walk ends at 30, Feed starts at 30 — back-to-back is not an overlap
# Expected: detect_conflicts() returns []
def test_back_to_back_tasks_are_not_conflicts():
    owner = Owner(name="Jordan", available_minutes=60)
    scheduler = Scheduler(owner)
    task_a = Task(title="Walk", duration_minutes=30, priority="high")
    task_b = Task(title="Feed", duration_minutes=10, priority="medium")
    scheduler.scheduled_tasks = [
        ScheduledTask(task=task_a, start_minute=0, end_minute=30),
        ScheduledTask(task=task_b, start_minute=30, end_minute=40),
    ]
    assert scheduler.detect_conflicts() == []

# Test: empty scheduled_tasks list has no conflicts
# Expected: detect_conflicts() returns []
def test_no_conflicts_when_no_tasks_scheduled():
    owner = Owner(name="Jordan", available_minutes=60)
    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []
