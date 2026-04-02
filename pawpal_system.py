from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    reason: str = ""
    pet: Pet | None = None  # reference back to owning pet

    def get_priority_score(self) -> int:
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_minute: int
    end_minute: int
    reasoning: str = ""


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.time_budget: int = owner.available_minutes  # derived from owner
        self.scheduled_tasks: list[ScheduledTask] = []

    def build_plan(self) -> list[ScheduledTask]:
        pass

    def explain_plan(self) -> str:
        pass
