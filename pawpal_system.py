from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Owner:
    """Represents a pet owner and their preferences/availability."""

    name: str
    available_start: str = "08:00"
    available_end: str = "18:00"
    preferences: List[str] = field(default_factory=list)

    def set_availability(self, start: str, end: str) -> None:
        """Set the owner's available time window."""
        raise NotImplementedError()

    def update_preferences(self, preferences: List[str]) -> None:
        """Replace or update owner preferences."""
        raise NotImplementedError()


@dataclass
class Pet:
    """Represents a pet and a light link back to its owner."""

    name: str
    species: str
    breed: Optional[str] = None
    owner: Optional[Owner] = None

    def update_info(self, **kwargs) -> None:
        """Update pet fields (name/species/breed/etc)."""
        raise NotImplementedError()


@dataclass
class CareTask:
    """A single care task to be scheduled for a pet."""

    name: str
    category: Optional[str] = None
    duration: int = 0  # minutes
    priority: str = "medium"  # low/medium/high
    preferred_time: Optional[str] = None
    pet: Optional[Pet] = None

    def update_task(self, **kwargs) -> None:
        """Update task attributes."""
        raise NotImplementedError()

    def validate(self) -> bool:
        """Validate required fields for scheduling."""
        raise NotImplementedError()


class Scheduler:
    """Scheduling engine interface. Holds tasks and produces a DailyPlan."""

    def __init__(self, owner: Owner, pets: Optional[List[Pet]] = None):
        self.owner = owner
        self.pets: List[Pet] = pets if pets is not None else []
        self.tasks: List[CareTask] = []

    def sort_tasks(self) -> None:
        """Sort tasks by priority, duration, or other heuristics."""
        raise NotImplementedError()

    def check_conflict(self, task: CareTask) -> bool:
        """Return True if `task` conflicts with existing schedule."""
        raise NotImplementedError()

    def generate_plan(self) -> "DailyPlan":
        """Generate and return a `DailyPlan` for the owner's pets."""
        raise NotImplementedError()

    def assign_times(self) -> None:
        """Assign concrete times to tasks in `self.tasks` based on availability."""
        raise NotImplementedError()


@dataclass
class DailyPlan:
    """Container for a day's scheduled and skipped tasks for a pet."""

    pet: Pet
    scheduled_tasks: List[CareTask] = field(default_factory=list)
    skipped_tasks: List[CareTask] = field(default_factory=list)
    explanation: Optional[str] = None

    def add_task(self, task: CareTask) -> None:
        raise NotImplementedError()

    def skip_task(self, task: CareTask) -> None:
        raise NotImplementedError()

    def explain_plan(self) -> str:
        raise NotImplementedError()

    def display_plan(self) -> str:
        raise NotImplementedError()


__all__ = ["Owner", "Pet", "CareTask", "Scheduler", "DailyPlan"]
