# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## Features

- **Priority-first scheduling** — Tasks are sorted high → medium → low before being added to the plan. Shorter duration breaks ties so more tasks fit within the available time window.
- **While-loop time budget enforcement** — `build_plan()` walks the sorted task list with a `while` loop, stopping naturally when time runs out or all tasks are evaluated. Two named booleans (`fits_in_budget`, `no_conflict`) keep the guard conditions readable.
- **Conflict detection** — `detect_conflicts()` flags overlapping time slots using the condition `a.start < b.end AND b.start < a.end`. A private `_would_conflict()` applies the same check inside `build_plan()` before each insertion, preventing conflicts from being scheduled in the first place.
- **Sorting by time** — `sort_by_time()` returns the scheduled plan in ascending `HH:MM` start-time order for clean display in the UI table.
- **Daily and weekly recurrence** — `Task.next_occurrence()` advances the due date by `timedelta(days=1)` or `timedelta(weeks=1)`. `Scheduler.mark_task_complete()` calls it automatically and registers the next occurrence with the pet.
- **Completion filtering** — `filter_tasks(completed=False)` returns only incomplete scheduled tasks; an optional `pet_name` argument narrows results to a specific pet.
- **Plain-English reasoning** — Every scheduled task includes a `reasoning` string explaining the pet name, priority score (out of 3), and minutes remaining when the task was added.
- **Owner-level task aggregation** — `Owner.get_all_tasks()` flattens pending tasks across all registered pets into a single list for the scheduler to consume.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ goes beyond a simple task list with three scheduling improvements:

**Priority-first planning with a while loop**
`Scheduler.build_plan()` sorts tasks by priority (high → medium → low) and walks the list with a `while` loop, adding each task that fits within the owner's available time. The loop exits naturally when time runs out — no `break` or `continue` needed, making the logic easy to read and trace.

**Recurring tasks (daily and weekly)**
`Task` now supports a `frequency` field (`"once"`, `"daily"`, `"weekly"`) and a `due_date`. When `Scheduler.mark_task_complete()` is called on a recurring task, it automatically creates the next occurrence and registers it with the pet — using Python's `timedelta(days=1)` for daily tasks and `timedelta(weeks=1)` for weekly tasks.

**Plain-English reasoning**
Every scheduled task includes a `reasoning` string explaining why it was chosen (priority score, pet it belongs to, and minutes remaining when it was added), so the plan is transparent, not just a list of times.

## Testing PawPal+

### Run the tests

```bash
python -m pytest test_pawpaw.py -v
```

### What the tests cover

36 tests across 7 areas:

| Area | What is verified |
|---|---|
| **Task addition** | Tasks are stored in the pet, back-reference to pet is set, multiple tasks persist |
| **Task completion** | `mark_complete()` sets the flag, completed tasks are excluded from pending and from the scheduled plan |
| **Priority sorting** | High priority is scheduled before medium, shorter tasks win tiebreakers, `get_priority_score` returns correct values |
| **Time budget** | Exact-fit tasks are scheduled, tasks 1 minute over budget are skipped, zero budget and empty task lists produce no crashes |
| **Recurring tasks** | `"once"` produces no next task, `"daily"` advances due date by 1 day, `"weekly"` advances by 7 days, next task is auto-registered with the pet |
| **Filter and sort** | `filter_tasks` by completion and pet name, `sort_by_time` returns ascending order |
| **Conflict detection** | Normal plans have no conflicts, overlapping slots are flagged, back-to-back slots are not flagged |

### Confidence level

★★★★☆ (4 / 5)

All 36 tests pass. Core behaviors — scheduling, priority ordering, time budget enforcement, recurring tasks, and conflict detection — are well covered. The one gap is that conflict detection inside `build_plan` can never actually fire in the current sequential design, so the guard has not been proven against a real runtime scenario. Confidence would reach 5 stars once tasks support fixed start times and a true scheduling conflict can be triggered end-to-end.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
