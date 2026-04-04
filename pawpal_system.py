from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    reason: str = ""
    pet: Pet | None = None
    completed: bool = False
    frequency: str = "once"  # "once", "daily", or "weekly"
    due_date: date | None = None

    def get_priority_score(self) -> int:
        """Returns a numeric score so tasks can be sorted: high=3, medium=2, low=1."""
        return {"high": 3, "medium": 2, "low": 1}.get(self.priority, 0)

    def mark_complete(self) -> None:
        """Mark this task as completed so it is excluded from future scheduling."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a new Task for the next occurrence, or None if frequency is 'once'.

        Uses timedelta to advance the due date:
          - 'daily'  -> due_date + timedelta(days=1)
          - 'weekly' -> due_date + timedelta(weeks=1)
        """
        if self.frequency == "once":
            return None

        base = self.due_date if self.due_date is not None else date.today()

        if self.frequency == "daily":
            next_due = base + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = base + timedelta(weeks=1)
        else:
            return None

        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            reason=self.reason,
            pet=self.pet,
            completed=False,
            frequency=self.frequency,
            due_date=next_due,
        )

    def __str__(self) -> str:
        """Return a short human-readable description of the task."""
        pet_label = f" [{self.pet.name}]" if self.pet else ""
        freq_label = f", {self.frequency}" if self.frequency != "once" else ""
        due_label = f", due {self.due_date}" if self.due_date else ""
        return f"{self.title}{pet_label} ({self.duration_minutes}min, {self.priority} priority{freq_label}{due_label})"


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task and link it back to this pet."""
        task.pet = self
        self.tasks.append(task)

    def pending_tasks(self) -> list[Task]:
        """Return only incomplete tasks."""
        return [t for t in self.tasks if not t.completed]

    def __str__(self) -> str:
        """Return a short human-readable description of the pet."""
        return f"{self.name} ({self.species})"


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Flatten all pending tasks across every pet."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.pending_tasks())
        return tasks

    def __str__(self) -> str:
        """Return a short human-readable description of the owner."""
        return f"{self.name} ({len(self.pets)} pet(s), {self.available_minutes} min available)"


@dataclass
class ScheduledTask:
    task: Task
    start_minute: int
    end_minute: int
    reasoning: str = ""

    def __str__(self) -> str:
        """Return the scheduled task as a formatted time-slot string with reasoning."""
        h_start, m_start = divmod(self.start_minute, 60)
        h_end, m_end = divmod(self.end_minute, 60)
        return (
            f"{self.task.title} — {h_start:02d}:{m_start:02d}–{h_end:02d}:{m_end:02d}"
            f"\n  Why: {self.reasoning}"
        )


class Scheduler:
    def __init__(self, owner: Owner):
        """Initialize the scheduler with an owner and derive the time budget from their availability."""
        self.owner = owner
        self.time_budget: int = owner.available_minutes
        self.scheduled_tasks: list[ScheduledTask] = []

    def build_plan(self) -> list[ScheduledTask]:
        """Sort pending tasks by priority and schedule them until time runs out.

        Tasks are sorted highest-to-lowest priority (with shorter duration as a
        tiebreaker). A while loop walks the sorted list and adds each task that
        still fits within the owner's available time. The loop exits naturally
        when all tasks have been checked or the time budget is exhausted.

        Returns:
            A list of ScheduledTask objects in the order they were scheduled,
            each with a start/end minute and a plain-English reasoning string.
        """
        self.scheduled_tasks = []

        sorted_tasks = sorted(
            self.owner.get_all_tasks(),
            key=lambda t: (-t.get_priority_score(), t.duration_minutes),
        )

        time_used = 0
        index = 0
        while index < len(sorted_tasks) and time_used < self.time_budget:
            task = sorted_tasks[index]
            new_end = time_used + task.duration_minutes

            fits_in_budget = new_end <= self.time_budget
            no_conflict = not self._would_conflict(time_used, new_end)

            if fits_in_budget and no_conflict:
                pet_prefix = f"For {task.pet.name}. " if task.pet else ""
                reasoning = (
                    f"{pet_prefix}Priority '{task.priority}' "
                    f"(score {task.get_priority_score()}/3). "
                    f"Fits within remaining time "
                    f"({self.time_budget - time_used} min left)."
                )
                self.scheduled_tasks.append(ScheduledTask(
                    task=task,
                    start_minute=time_used,
                    end_minute=new_end,
                    reasoning=reasoning,
                ))
                time_used += task.duration_minutes

            index += 1

        return self.scheduled_tasks

    def _would_conflict(self, start: int, end: int) -> bool:
        """Return True if a proposed [start, end) slot overlaps any already-scheduled task.

        Uses the same overlap condition as detect_conflicts:
            new task starts before existing ends  AND  existing starts before new task ends
        """
        return any(
            start < st.end_minute and st.start_minute < end
            for st in self.scheduled_tasks
        )

    def sort_by_time(self) -> list[ScheduledTask]:
        """Return scheduled tasks sorted by start time using HH:MM string format as the sort key."""
        def to_hhmm(st: ScheduledTask) -> str:
            h, m = divmod(st.start_minute, 60)
            return f"{h:02d}:{m:02d}"

        return sorted(self.scheduled_tasks, key=lambda st: to_hhmm(st))

    def filter_tasks(
        self,
        *,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[ScheduledTask]:
        """Filter scheduled tasks by completion status and/or pet name.

        Args:
            completed: If True, return only completed tasks. If False, only incomplete.
                       If None, completion status is not filtered.
            pet_name:  If provided, return only tasks belonging to the named pet.
        """
        results = self.scheduled_tasks

        if completed is not None:
            results = [st for st in results if st.task.completed == completed]

        if pet_name is not None:
            results = [
                st for st in results
                if st.task.pet is not None and st.task.pet.name.lower() == pet_name.lower()
            ]

        return results

    def detect_conflicts(self) -> list[tuple[ScheduledTask, ScheduledTask]]:
        """Check scheduled tasks for overlapping time slots.

        Two tasks conflict when one starts before the other has finished.
        The overlap condition is:  a.start < b.end  AND  b.start < a.end

        Returns:
            A list of (task_a, task_b) tuples for every conflicting pair found.
            Returns an empty list when there are no conflicts.
        """
        conflicts = []
        tasks = self.scheduled_tasks
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                a, b = tasks[i], tasks[j]
                if a.start_minute < b.end_minute and b.start_minute < a.end_minute:
                    conflicts.append((a, b))
        return conflicts

    def mark_task_complete(self, task: Task) -> Task | None:
        """Mark a task complete and, if it recurs, register the next occurrence with its pet.

        Returns the newly created next-occurrence Task, or None for one-time tasks.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None and task.pet is not None:
            task.pet.add_task(next_task)
        return next_task

    def explain_plan(self) -> str:
        """Return a human-readable summary of the scheduled plan."""
        if not self.scheduled_tasks:
            return "No tasks scheduled. Call build_plan() first or add tasks to your pets."

        lines = [f"Daily plan for {self.owner.name} ({self.time_budget} min available):\n"]
        for i, st in enumerate(self.scheduled_tasks, 1):
            lines.append(f"{i}. {st}")
        total = sum(st.task.duration_minutes for st in self.scheduled_tasks)
        lines.append(f"\nTotal time: {total} min of {self.time_budget} min used.")
        return "\n".join(lines)
