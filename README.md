# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

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
