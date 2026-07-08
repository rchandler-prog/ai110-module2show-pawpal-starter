"""Test suite for PawPal+ scheduling logic."""

import pytest
from pawpal_system import Owner, Pet, CareTask, Scheduler, DailyPlan, ScheduledTask


class TestCareTask:
    """Tests for CareTask class."""

    def test_validate_valid_task(self):
        """Test that a valid task passes validation."""
        task = CareTask(name="Walk", duration=20, priority="high")
        assert task.validate() is True

    def test_validate_invalid_duration(self):
        """Test that a task with zero/negative duration fails validation."""
        task = CareTask(name="Walk", duration=0, priority="high")
        assert task.validate() is False

    def test_validate_invalid_priority(self):
        """Test that a task with invalid priority fails validation."""
        task = CareTask(name="Walk", duration=20, priority="urgent")
        assert task.validate() is False

    def test_priority_score(self):
        """Test priority scoring."""
        low = CareTask(name="Play", duration=10, priority="low")
        med = CareTask(name="Feed", duration=10, priority="medium")
        high = CareTask(name="Meds", duration=10, priority="high")
        
        assert low.priority_score() == 1
        assert med.priority_score() == 2
        assert high.priority_score() == 3

    def test_update_task(self):
        """Test updating task attributes."""
        task = CareTask(name="Walk", duration=20, priority="low")
        task.update_task(duration=30, priority="high")
        assert task.duration == 30
        assert task.priority == "high"

    def test_daily_task_due_logic(self):
        """Test that daily tasks are due unless completed today."""
        task = CareTask(name="Feed", duration=10, priority="high", frequency="daily")
        assert task.is_due_on("2026-07-07") is True
        task.mark_complete(on_date="2026-07-07")
        assert task.is_due_on("2026-07-07") is False
        assert task.is_due_on("2026-07-08") is True

    def test_weekly_task_due_logic(self):
        """Test that weekly tasks become due after seven days."""
        task = CareTask(name="Groom", duration=25, priority="medium", frequency="weekly")
        task.mark_complete(on_date="2026-07-01")
        assert task.is_due_on("2026-07-06") is False
        assert task.is_due_on("2026-07-08") is True


class TestPet:
    """Tests for Pet class."""

    def test_pet_creation(self):
        """Test creating a pet."""
        pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever")
        assert pet.name == "Biscuit"
        assert pet.species == "dog"
        assert pet.breed == "Golden Retriever"

    def test_add_task_to_pet(self):
        """Test adding tasks to a pet."""
        pet = Pet(name="Mochi", species="cat")
        task1 = CareTask(name="Feed", duration=10, priority="high")
        task2 = CareTask(name="Play", duration=20, priority="medium")
        
        pet.add_task(task1)
        pet.add_task(task2)
        
        assert len(pet.tasks) == 2
        assert task1.pet == pet
        assert task2.pet == pet

    def test_remove_task_from_pet(self):
        """Test removing a task from a pet."""
        pet = Pet(name="Mochi", species="cat")
        task = CareTask(name="Feed", duration=10, priority="high")
        pet.add_task(task)
        pet.remove_task(task)
        
        assert len(pet.tasks) == 0

    def test_get_tasks(self):
        """Test retrieving all tasks for a pet."""
        pet = Pet(name="Biscuit", species="dog")
        task1 = CareTask(name="Walk", duration=30, priority="high")
        task2 = CareTask(name="Feed", duration=10, priority="high")
        
        pet.add_task(task1)
        pet.add_task(task2)
        
        tasks = pet.get_tasks()
        assert len(tasks) == 2
        assert task1 in tasks
        assert task2 in tasks

    def test_update_pet_info(self):
        """Test updating pet information."""
        pet = Pet(name="Mochi", species="cat", breed="Siamese")
        pet.update_info(name="Mochi Jr", breed="Persian")
        
        assert pet.name == "Mochi Jr"
        assert pet.breed == "Persian"
        assert pet.species == "cat"

    def test_mark_task_complete_creates_next_daily_task(self):
        """Test completing a daily task auto-creates the next occurrence."""
        pet = Pet(name="Biscuit", species="dog")
        pet.add_task(
            CareTask(
                name="Daily walk",
                duration=30,
                priority="high",
                frequency="daily",
            )
        )

        marked = pet.mark_task_complete("Daily walk", on_date="2026-07-07")
        assert marked is True
        assert len(pet.tasks) == 2
        assert pet.tasks[0].completed is True
        assert pet.tasks[1].name == "Daily walk"
        assert pet.tasks[1].due_date == "2026-07-08"
        assert pet.tasks[1].completed is False


class TestOwner:
    """Tests for Owner class."""

    def test_owner_creation(self):
        """Test creating an owner."""
        owner = Owner(name="Jordan", available_start="08:00", available_end="18:00")
        assert owner.name == "Jordan"
        assert owner.available_start == "08:00"
        assert owner.available_end == "18:00"

    def test_add_pet_to_owner(self):
        """Test adding pets to an owner."""
        owner = Owner(name="Jordan")
        pet1 = Pet(name="Biscuit", species="dog")
        pet2 = Pet(name="Mochi", species="cat")
        
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        
        assert len(owner.pets) == 2
        assert pet1.owner == owner
        assert pet2.owner == owner

    def test_get_all_tasks(self):
        """Test retrieving all tasks from all pets."""
        owner = Owner(name="Jordan")
        
        pet1 = Pet(name="Biscuit", species="dog")
        pet1.add_task(CareTask(name="Morning walk", duration=30, priority="high"))
        pet1.add_task(CareTask(name="Feed", duration=10, priority="high"))
        
        pet2 = Pet(name="Mochi", species="cat")
        pet2.add_task(CareTask(name="Litter box clean", duration=5, priority="medium"))
        
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        
        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 3

    def test_set_availability(self):
        """Test setting owner availability."""
        owner = Owner(name="Jordan")
        owner.set_availability("09:00", "17:00")
        
        assert owner.available_start == "09:00"
        assert owner.available_end == "17:00"

    def test_update_preferences(self):
        """Test updating owner preferences."""
        owner = Owner(name="Jordan")
        prefs = ["outdoor", "interactive"]
        owner.update_preferences(prefs)
        
        assert owner.preferences == prefs

    def test_get_tasks_by_pet(self):
        """Test filtering tasks by pet name."""
        owner = Owner(name="Jordan")
        dog = Pet(name="Biscuit", species="dog")
        cat = Pet(name="Mochi", species="cat")
        dog.add_task(CareTask(name="Walk", duration=30, priority="high"))
        cat.add_task(CareTask(name="Feed", duration=10, priority="high"))
        owner.add_pet(dog)
        owner.add_pet(cat)

        dog_tasks = owner.get_tasks_by_pet("Biscuit")
        assert len(dog_tasks) == 1
        assert dog_tasks[0].name == "Walk"

    def test_get_tasks_by_status(self):
        """Test filtering tasks by completion status."""
        owner = Owner(name="Jordan")
        pet = Pet(name="Biscuit", species="dog")
        done = CareTask(name="Feed", duration=10, priority="high")
        todo = CareTask(name="Walk", duration=20, priority="medium")
        done.mark_complete(on_date="2026-07-07")
        pet.add_task(done)
        pet.add_task(todo)
        owner.add_pet(pet)

        completed = owner.get_tasks_by_status(True)
        pending = owner.get_tasks_by_status(False)
        assert len(completed) == 1
        assert completed[0].name == "Feed"
        assert len(pending) == 1
        assert pending[0].name == "Walk"


class TestScheduler:
    """Tests for Scheduler class."""

    def test_scheduler_creation(self):
        """Test creating a scheduler."""
        owner = Owner(name="Jordan")
        scheduler = Scheduler(owner)
        assert scheduler.owner == owner

    def test_time_conversion(self):
        """Test time string to minutes conversion."""
        owner = Owner(name="Jordan")
        scheduler = Scheduler(owner)
        
        assert scheduler.time_to_minutes("08:00") == 480  # 8*60
        assert scheduler.time_to_minutes("12:30") == 750  # 12*60 + 30
        assert scheduler.time_to_minutes("18:00") == 1080  # 18*60

    def test_minutes_to_time_conversion(self):
        """Test minutes to time string conversion."""
        owner = Owner(name="Jordan")
        scheduler = Scheduler(owner)
        
        assert scheduler.minutes_to_time(480) == "08:00"
        assert scheduler.minutes_to_time(750) == "12:30"
        assert scheduler.minutes_to_time(1080) == "18:00"

    def test_get_available_minutes(self):
        """Test calculating available minutes."""
        owner = Owner(name="Jordan", available_start="08:00", available_end="18:00")
        scheduler = Scheduler(owner)
        
        available = scheduler.get_available_minutes()
        assert available == 600  # 10 hours

    def test_check_conflict_no_overlap(self):
        """Test conflict detection when no overlap exists."""
        owner = Owner(name="Jordan")
        scheduler = Scheduler(owner)
        
        occupied = [(480, 510), (600, 630)]  # 8-8:30, 10-10:30
        has_conflict = scheduler.check_conflict(520, 50, occupied)  # 8:40-9:30
        
        assert has_conflict is False

    def test_check_conflict_with_overlap(self):
        """Test conflict detection when overlap exists."""
        owner = Owner(name="Jordan")
        scheduler = Scheduler(owner)
        
        occupied = [(480, 510)]  # 8-8:30
        has_conflict = scheduler.check_conflict(500, 50, occupied)  # 8:20-9:10 (overlaps!)
        
        assert has_conflict is True

    def test_sort_tasks_by_priority(self):
        """Test task sorting by priority."""
        owner = Owner(name="Jordan")
        pet = Pet(name="Biscuit", species="dog")
        
        task_low = CareTask(name="Play", duration=20, priority="low")
        task_high = CareTask(name="Meds", duration=5, priority="high")
        task_med = CareTask(name="Feed", duration=10, priority="medium")
        
        pet.add_task(task_low)
        pet.add_task(task_high)
        pet.add_task(task_med)
        owner.add_pet(pet)
        
        scheduler = Scheduler(owner)
        scheduler.load_tasks()
        scheduler.sort_tasks()
        
        # Should be: high, medium, low (by priority score)
        assert scheduler.tasks[0] == task_high
        assert scheduler.tasks[1] == task_med
        assert scheduler.tasks[2] == task_low

    def test_sort_tasks_by_preferred_time(self):
        """Test preferred-time tasks are ordered earlier than non-preferred tasks."""
        owner = Owner(name="Jordan")
        scheduler = Scheduler(owner)

        task_no_pref = CareTask(name="Play", duration=20, priority="high")
        task_pref_late = CareTask(name="Brush", duration=10, priority="low", preferred_time="09:00")
        task_pref_early = CareTask(name="Meds", duration=5, priority="medium", preferred_time="08:15")

        ordered = scheduler.sort_task_list([task_no_pref, task_pref_late, task_pref_early])
        assert ordered[0] == task_pref_early
        assert ordered[1] == task_pref_late
        assert ordered[2] == task_no_pref

    def test_sort_by_time_method(self):
        """Test explicit sort_by_time() ordering in HH:MM format."""
        owner = Owner(name="Jordan")
        scheduler = Scheduler(owner)
        t1 = CareTask(name="A", duration=5, priority="low", preferred_time="09:10")
        t2 = CareTask(name="B", duration=5, priority="low", preferred_time="08:45")
        t3 = CareTask(name="C", duration=5, priority="low")

        ordered = scheduler.sort_by_time([t1, t2, t3])
        assert [t.name for t in ordered] == ["B", "A", "C"]

    def test_filter_tasks_method(self):
        """Test scheduler-side filtering by pet and completion."""
        owner = Owner(name="Jordan")
        scheduler = Scheduler(owner)

        dog = Pet(name="Biscuit", species="dog")
        cat = Pet(name="Mochi", species="cat")
        t1 = CareTask(name="Walk", duration=20, priority="high")
        t2 = CareTask(name="Feed", duration=10, priority="high")
        t3 = CareTask(name="Play", duration=10, priority="low")
        t1.mark_complete(on_date="2026-07-07")

        dog.add_task(t1)
        dog.add_task(t2)
        cat.add_task(t3)
        tasks = dog.get_tasks() + cat.get_tasks()

        dog_pending = scheduler.filter_tasks(tasks, pet_name="Biscuit", completed=False)
        assert len(dog_pending) == 1
        assert dog_pending[0].name == "Feed"

    def test_generate_plan_basic(self):
        """Test basic plan generation."""
        owner = Owner(name="Jordan", available_start="08:00", available_end="09:00")
        pet = Pet(name="Biscuit", species="dog")
        
        task1 = CareTask(name="Morning walk", duration=30, priority="high")
        task2 = CareTask(name="Feed", duration=15, priority="high")
        task3 = CareTask(name="Play", duration=20, priority="medium")
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        owner.add_pet(pet)
        
        scheduler = Scheduler(owner)
        plans = scheduler.generate_plan()
        
        assert len(plans) == 1
        plan = plans[0]
        assert plan.pet == pet
        assert len(plan.scheduled_tasks) == 2  # Walk (30) + Feed (15) = 45 min (fits in 60)
        assert len(plan.skipped_tasks) == 1  # Play (20) doesn't fit

    def test_generate_plan_multiple_pets(self):
        """Test plan generation for multiple pets."""
        owner = Owner(name="Jordan", available_start="08:00", available_end="09:00")
        
        pet1 = Pet(name="Biscuit", species="dog")
        pet1.add_task(CareTask(name="Walk", duration=30, priority="high"))
        
        pet2 = Pet(name="Mochi", species="cat")
        pet2.add_task(CareTask(name="Feed", duration=15, priority="high"))
        
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        
        scheduler = Scheduler(owner)
        plans = scheduler.generate_plan()
        
        assert len(plans) == 2
        assert plans[0].pet == pet1
        assert plans[1].pet == pet2

    def test_generate_plan_respects_preferred_time_when_possible(self):
        """Test preferred time is used if slot is available."""
        owner = Owner(name="Jordan", available_start="08:00", available_end="10:00")
        pet = Pet(name="Biscuit", species="dog")
        pet.add_task(CareTask(name="Feed", duration=10, priority="high", preferred_time="08:30"))
        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        plans = scheduler.generate_plan()
        assert plans[0].scheduled_tasks[0].start_time == "08:30"

    def test_generate_plan_conflict_fallback_to_next_slot(self):
        """Test conflicting preferred times use next available slot."""
        owner = Owner(name="Jordan", available_start="08:00", available_end="09:00")
        pet = Pet(name="Biscuit", species="dog")
        pet.add_task(CareTask(name="Walk", duration=30, priority="high", preferred_time="08:00"))
        pet.add_task(CareTask(name="Feed", duration=10, priority="high", preferred_time="08:00"))
        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        plans = scheduler.generate_plan()
        scheduled = plans[0].scheduled_tasks
        assert len(scheduled) == 2
        assert scheduled[0].start_time == "08:00"
        assert scheduled[1].start_time == scheduled[0].end_time

    def test_generate_plan_skips_not_due_weekly_task(self):
        """Test weekly task is skipped if completed within last seven days."""
        owner = Owner(name="Jordan", available_start="08:00", available_end="09:00")
        pet = Pet(name="Mochi", species="cat")
        weekly = CareTask(name="Groom", duration=20, priority="medium", frequency="weekly")
        weekly.mark_complete(on_date="2026-07-05")
        pet.add_task(weekly)
        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        plans = scheduler.generate_plan(date_str="2026-07-07")
        assert len(plans[0].scheduled_tasks) == 0
        assert len(plans[0].skipped_tasks) == 0

    def test_detect_conflicts_returns_warning(self):
        """Test conflict detector returns warning messages for overlaps."""
        owner = Owner(name="Jordan")
        scheduler = Scheduler(owner)

        pet1 = Pet(name="Biscuit", species="dog")
        pet2 = Pet(name="Mochi", species="cat")
        plan1 = DailyPlan(pet=pet1)
        plan2 = DailyPlan(pet=pet2)

        task1 = CareTask(name="Walk", duration=30, priority="high", pet=pet1)
        task2 = CareTask(name="Feed", duration=15, priority="high", pet=pet2)
        plan1.add_task(ScheduledTask(task=task1, start_time="08:00", end_time="08:30"))
        plan2.add_task(ScheduledTask(task=task2, start_time="08:10", end_time="08:25"))

        warnings = scheduler.detect_conflicts([plan1, plan2])
        assert len(warnings) == 1
        assert "Conflict:" in warnings[0]

    def test_daily_plan_display(self):
        """Test daily plan display/explanation."""
        owner = Owner(name="Jordan", available_start="08:00", available_end="09:00")
        pet = Pet(name="Biscuit", species="dog")
        
        task = CareTask(name="Morning walk", duration=30, priority="high")
        pet.add_task(task)
        owner.add_pet(pet)
        
        scheduler = Scheduler(owner)
        plans = scheduler.generate_plan()
        plan = plans[0]
        
        display = plan.display_plan()
        assert "Biscuit" in display
        assert "Morning walk" in display


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
