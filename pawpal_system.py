from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Tuple


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
    frequency: str = "once"  # once, daily, weekly
    last_completed_on: Optional[str] = None  # ISO date string YYYY-MM-DD
    due_date: Optional[str] = None  # ISO date string YYYY-MM-DD

    def update_task(self, **kwargs) -> None:
        """Update task attributes (name, duration, priority, etc)."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_complete(self, on_date: Optional[str] = None) -> None:
        """Mark this task as completed and record completion date."""
        self.completed = True
        self.last_completed_on = on_date or date.today().isoformat()

    def validate(self) -> bool:
        """Validate required fields for scheduling."""
        if not self.name or self.duration <= 0:
            return False
        if self.priority not in ["low", "medium", "high"]:
            return False
        if self.frequency not in ["once", "daily", "weekly"]:
            return False
        return True

    def priority_score(self) -> int:
        """Return numeric priority (higher = more urgent)."""
        priority_map = {"low": 1, "medium": 2, "high": 3}
        return priority_map.get(self.priority, 2)

    def is_due_on(self, date_str: Optional[str] = None) -> bool:
        """Return whether this task is due on the given date."""
        target_date = date.fromisoformat(date_str) if date_str else date.today()

        if self.due_date:
            return target_date >= date.fromisoformat(self.due_date)

        if self.frequency == "once":
            return not self.completed

        if self.frequency == "daily":
            return self.last_completed_on != target_date.isoformat()

        if self.frequency == "weekly":
            if not self.last_completed_on:
                return True
            last_done = date.fromisoformat(self.last_completed_on)
            return (target_date - last_done) >= timedelta(days=7)

        return True

    def create_next_occurrence(self, from_date: Optional[str] = None) -> Optional["CareTask"]:
        """Create the next daily or weekly occurrence after completion."""
        if self.frequency not in ["daily", "weekly"]:
            return None

        base_date = date.fromisoformat(from_date) if from_date else date.today()
        delta_days = 1 if self.frequency == "daily" else 7
        next_due = (base_date + timedelta(days=delta_days)).isoformat()

        return CareTask(
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            preferred_time=self.preferred_time,
            pet=self.pet,
            completed=False,
            frequency=self.frequency,
            last_completed_on=None,
            due_date=next_due,
        )


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

    def mark_task_complete(self, task_name: str, on_date: Optional[str] = None) -> bool:
        """Mark first matching open task complete and enqueue next recurring task."""
        target = task_name.strip().lower()
        for task in self.tasks:
            if task.name.lower() == target and not task.completed:
                completion_date = on_date or date.today().isoformat()
                task.mark_complete(completion_date)
                next_task = task.create_next_occurrence(completion_date)
                if next_task:
                    self.add_task(next_task)
                return True
        return False


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

    def get_tasks_by_pet(self, pet_name: str) -> List[CareTask]:
        """Return tasks that belong to a specific pet by name."""
        normalized = pet_name.strip().lower()
        return [
            task
            for task in self.get_all_tasks()
            if task.pet is not None and task.pet.name.lower() == normalized
        ]

    def get_tasks_by_status(self, completed: bool) -> List[CareTask]:
        """Return tasks filtered by completion status."""
        return [task for task in self.get_all_tasks() if task.completed == completed]

    def get_tasks_filtered(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
    ) -> List[CareTask]:
        """Return tasks filtered by optional pet, completion, and priority."""
        filtered = self.get_all_tasks()

        if pet_name is not None:
            normalized = pet_name.strip().lower()
            filtered = [
                task
                for task in filtered
                if task.pet is not None and task.pet.name.lower() == normalized
            ]

        if completed is not None:
            filtered = [task for task in filtered if task.completed == completed]

        if priority is not None:
            filtered = [task for task in filtered if task.priority == priority]

        return filtered

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
        """Return a concise debug string for a scheduled task."""
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
        """Initialize scheduler state for a single owner."""
        self.owner = owner
        self.tasks: List[CareTask] = []
        self.scheduled_tasks: List[ScheduledTask] = []

    def load_tasks(self) -> None:
        """Retrieve all tasks from the owner's pets."""
        self.tasks = self.owner.get_all_tasks()

    def sort_tasks(self) -> None:
        """Sort by preferred time, then priority, then shorter duration."""

        def task_sort_key(task: CareTask) -> tuple:
            preferred_minute = self.time_to_minutes(task.preferred_time) if task.preferred_time else 10**9
            has_no_preferred_time = task.preferred_time is None
            return (has_no_preferred_time, preferred_minute, -task.priority_score(), task.duration)

        self.tasks.sort(key=task_sort_key)

    def sort_by_time(self, tasks: List[CareTask]) -> List[CareTask]:
        """Return tasks sorted by HH:MM preferred_time, with missing times last."""
        return sorted(
            tasks,
            key=lambda task: (
                task.preferred_time is None,
                self.time_to_minutes(task.preferred_time) if task.preferred_time else 10**9,
            ),
        )

    def filter_tasks(
        self,
        tasks: List[CareTask],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[CareTask]:
        """Return tasks filtered by pet name and/or completion status."""
        filtered = tasks
        if pet_name is not None:
            normalized = pet_name.strip().lower()
            filtered = [
                task
                for task in filtered
                if task.pet is not None and task.pet.name.lower() == normalized
            ]
        if completed is not None:
            filtered = [task for task in filtered if task.completed == completed]
        return filtered

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

    def check_conflict(self, start_min: int, duration: int, occupied: List[Tuple[int, int]]) -> bool:
        """Check if a time slot [start_min, start_min+duration) conflicts with occupied slots."""
        task_end = start_min + duration
        for occ_start, occ_end in occupied:
            if not (task_end <= occ_start or start_min >= occ_end):
                return True
        return False

    def expand_recurring_tasks(self, tasks: List[CareTask], date_str: Optional[str] = None) -> List[CareTask]:
        """Return only tasks that are due for the given date."""
        return [task for task in tasks if task.is_due_on(date_str)]

    def find_first_fit(
        self,
        duration: int,
        window_start: int,
        window_end: int,
        occupied: List[Tuple[int, int]],
    ) -> Optional[int]:
        """Find earliest non-conflicting start minute in the owner's time window."""
        sorted_occupied = sorted(occupied)
        candidate = window_start

        for occ_start, occ_end in sorted_occupied:
            if candidate + duration <= occ_start:
                return candidate
            candidate = max(candidate, occ_end)

        if candidate + duration <= window_end:
            return candidate
        return None

    def find_slot_for_task(
        self,
        task: CareTask,
        window_start: int,
        window_end: int,
        occupied: List[Tuple[int, int]],
    ) -> Optional[int]:
        """Return best start minute, preferring preferred_time and falling back to first-fit."""
        if task.preferred_time:
            preferred_start = self.time_to_minutes(task.preferred_time)
            preferred_end = preferred_start + task.duration
            if (
                window_start <= preferred_start
                and preferred_end <= window_end
                and not self.check_conflict(preferred_start, task.duration, occupied)
            ):
                return preferred_start

        return self.find_first_fit(task.duration, window_start, window_end, occupied)

    def sort_task_list(self, tasks: List[CareTask]) -> List[CareTask]:
        """Return a sorted copy of tasks using scheduler sort rules."""
        return sorted(
            tasks,
            key=lambda task: (
                task.preferred_time is None,
                self.time_to_minutes(task.preferred_time) if task.preferred_time else 10**9,
                -task.priority_score(),
                task.duration,
            ),
        )

    def generate_plan(self, date_str: Optional[str] = None) -> List[DailyPlan]:
        """Generate a daily plan for each of the owner's pets."""
        plans = []

        for pet in self.owner.get_pets():
            plan = DailyPlan(pet=pet)
            pet_tasks = pet.get_tasks()
            due_tasks = self.expand_recurring_tasks(pet_tasks, date_str)
            sorted_tasks = self.sort_task_list(due_tasks)

            occupied_slots: List[Tuple[int, int]] = []
            start_min = self.time_to_minutes(self.owner.available_start)
            end_min = self.time_to_minutes(self.owner.available_end)

            for task in sorted_tasks:
                slot_start = self.find_slot_for_task(task, start_min, end_min, occupied_slots)
                if slot_start is None:
                    plan.skip_task(task)
                    continue

                task_end = slot_start + task.duration
                plan.add_task(
                    ScheduledTask(
                        task=task,
                        start_time=self.minutes_to_time(slot_start),
                        end_time=self.minutes_to_time(task_end),
                    )
                )
                occupied_slots.append((slot_start, task_end))

            plan.explanation = f"Scheduled {len(plan.scheduled_tasks)} task(s) for {pet.name}. Skipped {len(plan.skipped_tasks)} task(s) due to time constraints."
            plans.append(plan)

        return plans

    def assign_times(self) -> List[DailyPlan]:
        """Alias for generate_plan() — produces schedules with concrete times."""
        return self.generate_plan()

    def detect_conflicts(self, plans: List[DailyPlan]) -> List[str]:
        """Return lightweight warnings for overlapping scheduled tasks."""
        scheduled_items: List[Tuple[str, ScheduledTask, int, int]] = []
        for plan in plans:
            for item in plan.scheduled_tasks:
                start_min = self.time_to_minutes(item.start_time)
                end_min = self.time_to_minutes(item.end_time)
                scheduled_items.append((plan.pet.name, item, start_min, end_min))

        warnings: List[str] = []
        for index, (pet_a, item_a, start_a, end_a) in enumerate(scheduled_items):
            for pet_b, item_b, start_b, end_b in scheduled_items[index + 1 :]:
                overlaps = not (end_a <= start_b or end_b <= start_a)
                if overlaps:
                    warnings.append(
                        f"Conflict: {pet_a} '{item_a.task.name}' ({item_a.start_time}-{item_a.end_time}) overlaps with {pet_b} '{item_b.task.name}' ({item_b.start_time}-{item_b.end_time})."
                    )

        return warnings


__all__ = ["Owner", "Pet", "CareTask", "Scheduler", "DailyPlan", "ScheduledTask"]
