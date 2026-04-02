# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PawPal+ is a Module 2 student project — a Streamlit-based pet care planning assistant. The starter app in `app.py` is intentionally thin: it provides a working UI shell with no scheduling logic. The student's job is to design and implement the backend scheduling system and wire it into the UI.

## Setup and Commands

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Run all tests
pytest

# Run a single test file
pytest tests/test_scheduler.py

# Run a single test by name
pytest -k "test_high_priority_task_is_scheduled_first"
```

## Architecture

The project is structured as a single-file Streamlit app (`app.py`) that needs to be extended with backend logic. The intended architecture:

- **`app.py`** — Streamlit UI. Collects owner/pet info and tasks from the user, calls the scheduler, and displays the resulting plan.
- **`pawpal_system.py`** (to be created) — Core domain classes: `Owner`, `Pet`, `Task`, `Scheduler` (or similar). The scheduler takes a list of tasks with durations, priorities, and constraints and produces an ordered daily plan with reasoning.
- **`tests/`** (to be created) — pytest tests for scheduling behavior.

The `reflection.md` file is a student deliverable — do not modify it; the student fills it out.

## Key Constraints

- The scheduler must consider at minimum: task duration, priority, and time available.
- The plan output should explain *why* each task was chosen and ordered as it was.
- `requirements.txt` only includes `streamlit` and `pytest` — do not add heavyweight dependencies.
