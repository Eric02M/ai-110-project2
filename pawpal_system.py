from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    reason: str = ""

    def get_priority_score(self) -> int:
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_minute: int
    end_minute: int
    reasoning: str = ""


class Scheduler:
    def __init__(self, owner: Owner, time_budget: int):
        self.owner = owner
        self.time_budget = time_budget
        self.scheduled_tasks: list[ScheduledTask] = []

    def build_plan(self) -> list[ScheduledTask]:
        pass

    def explain_plan(self) -> str:
        pass
