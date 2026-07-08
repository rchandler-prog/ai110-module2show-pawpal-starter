from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import time, timedelta


@dataclass
class CareTask:
    """A single care task to be scheduled for a pet."""

    name: str
    category: Optional[str] = None
    duration: int = 0  # minutes
    priority: str = "medium"  # low/medium/high
    preferred_time: Optional[str] = None
    pet: Optional["Pet"] = None
    completed: bool = False

    def update_task(self, **kwargs) -> None:
        """Update task attributes (name, duration, priority, etc)."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def validate(self) -> bool:
        """Validate required fields for scheduling."""
        if not self.name or self.duration <= 0:
            return False
        if self.priority not in ["low", "medium", "high"]:
            return False
        return True

    def priority_score(self) -> int:
        """Return numeric priority (higher = more urgent)."""
        priority_map = {"low": 1, "medium": 2, "high": 3}
        return priority_map.get(self.priority, 2)


@dataclass
class Pet:
    """Represents a pet and a light link back to its owner."""

    name: str
    species: str
    breed: Optional[str] = None
    owner: Optional["Owner"] = None
    tasks: List[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add a task to this pet's task list."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: CareTask) -> None:
        """Remove a task from this pet's task list."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self) -> List[CareTask]:
        """Return all tasks for this pet."""
        return self.tasks.copy()

    def update_info(self, **kwargs) -> None:
        """Update pet fields (name/species/breed/etc)."""
        for key in ["name", "species", "breed"]:
            if key in kwargs:
                setattr(self, key, kwargs[key])


@dataclass
class Owner:
    """Represents a pet owner and their preferences/availability."""

    name: str
    available_start: str = "08:00"
    available_end: str = "18:00"
    preferences: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        pet.owner = self
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner's pet list."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return self.pets.copy()

    def get_all_tasks(self) -> List[CareTask]:
        """Aggregate and return all tasks from all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def set_availability(self, start: str, end: str) -> None:
        """Set the owner's available time window (format: 'HH:MM')."""
        self.available_start = start
        self.available_end = end

    def update_preferences(self, preferences: List[str]) -> None:
        """Replace or update owner preferences."""
        self.preferences = preferences.copy()


@dataclass
class ScheduledTask:
    """A task with an assigned time slot."""

    task: CareTask
    start_time: str  # format "HH:MM"
    end_time: str    # format "HH:MM"

    def __repr__(self) -> str:
        return f"{self.task.name} ({self.start_time} - {self.end_time})"


@dataclass
class DailyPlan:
    """Container for a day's scheduled and skipped tasks for a pet."""

    pet: Pet
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    skipped_tasks: List[CareTask] = field(default_factory=list)
    explanation: Optional[str] = None

    def add_task(self, scheduled_task: ScheduledTask) -> None:
        """Add a scheduled task to the plan."""
        self.scheduled_tasks.append(scheduled_task)

    def skip_task(self, task: CareTask) -> None:
        """Mark a task as skipped."""
        if task not in self.skipped_tasks:
            self.skipped_tasks.append(task)

    def explain_plan(self) -> str:
        """Generate an explanation of why tasks were chosen/skipped."""
        lines = [f"Daily plan for {self.pet.name} ({self.pet.species}):"]
        
        if self.scheduled_tasks:
            lines.append("Scheduled tasks:")
            for st in self.scheduled_tasks:
                lines.append(f"  {st.start_time} - {st.end_time}: {st.task.name} ({st.task.duration} min) [priority: {st.task.priority}]")
        else:
            lines.append("  No tasks scheduled.")

        if self.skipped_tasks:
            lines.append("Skipped tasks (not enough time):")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.name} ({task.duration} min) [priority: {task.priority}]")

        return "\n".join(lines)

    def display_plan(self) -> str:
        """Return a user-friendly display of the plan."""
        return self.explain_plan()


class Scheduler:
    """Scheduling engine: retrieves tasks from owner's pets and produces a daily plan."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: List[CareTask] = []
        self.scheduled_tasks: List[ScheduledTask] = []

    def load_tasks(self) -> None:
        """Retrieve all tasks from the owner's pets."""
        self.tasks = self.owner.get_all_tasks()

    def sort_tasks(self) -> None:
        """Sort tasks by priority (high first), then by duration (shorter first)."""
        self.tasks.sort(key=lambda t: (-t.priority_score(), t.duration))

    def time_to_minutes(self, time_str: str) -> int:
        """Convert 'HH:MM' string to minutes since midnight."""
        parts = time_str.split(":")
        hours, minutes = int(parts[0]), int(parts[1])
        return hours * 60 + minutes

    def minutes_to_time(self, minutes: int) -> str:
        """Convert minutes since midnight back to 'HH:MM' string."""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    def get_available_minutes(self) -> int:
        """Calculate total available minutes in the day."""
        start = self.time_to_minutes(self.owner.available_start)
        end = self.time_to_minutes(self.owner.available_end)
        return end - start

    def check_conflict(self, start_min: int, duration: int, occupied: List[tuple]) -> bool:
        """Check if a time slot [start_min, start_min+duration) conflicts with occupied slots."""
        task_end = start_min + duration
        for occ_start, occ_end in occupied:
            if not (task_end <= occ_start or start_min >= occ_end):
                return True
        return False

    def generate_plan(self) -> List[DailyPlan]:
        """Generate a daily plan for each of the owner's pets."""
        self.load_tasks()
        self.sort_tasks()

        plans = []
        for pet in self.owner.get_pets():
            plan = DailyPlan(pet=pet)
            pet_tasks = [t for t in self.tasks if t.pet == pet]

            occupied_slots = []
            start_min = self.time_to_minutes(self.owner.available_start)
            end_min = self.time_to_minutes(self.owner.available_end)

            for task in pet_tasks:
                if self.check_conflict(start_min, task.duration, occupied_slots):
                    # Skip tasks that don't fit
                    plan.skip_task(task)
                else:
                    # Schedule the task
                    task_end = start_min + task.duration
                    if task_end <= end_min:
                        start_time = self.minutes_to_time(start_min)
                        end_time = self.minutes_to_time(task_end)
                        scheduled = ScheduledTask(task=task, start_time=start_time, end_time=end_time)
                        plan.add_task(scheduled)
                        occupied_slots.append((start_min, task_end))
                        start_min = task_end
                    else:
                        plan.skip_task(task)

            plan.explanation = f"Scheduled {len(plan.scheduled_tasks)} task(s) for {pet.name}. Skipped {len(plan.skipped_tasks)} task(s) due to time constraints."
            plans.append(plan)

        return plans

    def assign_times(self) -> List[DailyPlan]:
        """Alias for generate_plan() — produces schedules with concrete times."""
        return self.generate_plan()


__all__ = ["Owner", "Pet", "CareTask", "Scheduler", "DailyPlan", "ScheduledTask"]
