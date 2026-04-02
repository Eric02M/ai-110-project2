from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    reason: str = ""
    pet: Pet | None = None
    completed: bool = False

    def get_priority_score(self) -> int:
        """Returns a numeric score so tasks can be sorted: high=3, medium=2, low=1."""
        return {"high": 3, "medium": 2, "low": 1}.get(self.priority, 0)

    def mark_complete(self) -> None:
        """Mark this task as completed so it is excluded from future scheduling."""
        self.completed = True

    def __str__(self) -> str:
        """Return a short human-readable description of the task."""
        pet_label = f" [{self.pet.name}]" if self.pet else ""
        return f"{self.title}{pet_label} ({self.duration_minutes}min, {self.priority} priority)"


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
        """Sort pending tasks by priority and greedily schedule those that fit within available time."""
        self.scheduled_tasks = []
        all_tasks = self.owner.get_all_tasks()

        # Sort by priority descending, then by duration ascending as a tiebreaker
        sorted_tasks = sorted(
            all_tasks,
            key=lambda t: (-t.get_priority_score(), t.duration_minutes),
        )

        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration_minutes > self.time_budget:
                continue  # skip tasks that no longer fit

            reasoning = (
                f"Priority '{task.priority}' (score {task.get_priority_score()}/3). "
                f"Fits within remaining time "
                f"({self.time_budget - time_used} min left)."
            )
            if task.pet:
                reasoning = f"For {task.pet.name}. " + reasoning

            scheduled = ScheduledTask(
                task=task,
                start_minute=time_used,
                end_minute=time_used + task.duration_minutes,
                reasoning=reasoning,
            )
            self.scheduled_tasks.append(scheduled)
            time_used += task.duration_minutes

        return self.scheduled_tasks

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
