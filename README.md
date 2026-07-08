# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan care tasks for their pet(s), organize them intelligently, and understand why the schedule was chosen.

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

## Features

- **Sorting by time:** Orders tasks with `Scheduler.sort_by_time()` so tasks with earlier preferred times appear first.
- **Filtering by pet/status:** Uses `Scheduler.filter_tasks()` and `Owner.get_tasks_filtered()` to narrow tasks by pet name or completion status.
- **Recurring tasks:** Uses `CareTask.mark_complete()` and `CareTask.create_next_occurrence()` to regenerate daily and weekly tasks.
- **Conflict warnings:** Uses `Scheduler.detect_conflicts()` to warn about overlapping scheduled tasks instead of failing silently.
- **Per-pet daily plans:** Uses `Scheduler.generate_plan()` and `DailyPlan.display_plan()` to show a schedule for each pet.

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

## 🖥️ Sample Output

```text
SORTED TASKS FOR BISCUIT (by preferred time):
- 08:00 | Feed | high
- 08:30 | Morning walk | high
- 09:30 | Play | medium

FILTERED TASKS (Biscuit + incomplete):
- Morning walk (completed=False)
- Feed (completed=False)
- Play (completed=False)

RECURRING TASK AUTOMATION:
- Morning walk: completed=True, due_date=None, frequency=daily
- Morning walk: completed=False, due_date=2026-07-08, frequency=daily

Today's Schedule:

Daily plan for Biscuit (dog):
Scheduled tasks:
  08:00 - 08:10: Feed (10 min) [priority: high]
  09:30 - 09:50: Play (20 min) [priority: medium]

----------------------------------------

Daily plan for Mochi (cat):
Scheduled tasks:
  08:00 - 08:10: Feed (10 min) [priority: high]
  08:10 - 08:25: Litter clean (15 min) [priority: medium]

----------------------------------------

CONFLICT WARNINGS:
! Conflict: Biscuit 'Feed' (08:00-08:10) overlaps with Mochi 'Feed' (08:00-08:10).
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest
```

This automated suite validates core scheduler behavior, including:

- chronological sorting by task time,
- filtering by pet and completion status,
- recurring task generation after completion,
- conflict detection warnings,
- plan generation and edge cases (no tasks / constrained time windows).

Successful test output:

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-7.4.4, pluggy-1.0.0
rootdir: /Users/tigerchandler/fellowship-readiness-tracker/ai110-module2show-pawpal-starter
plugins: anyio-4.2.0
collected 37 items

tests/test_pawpal.py .....................................               [100%]

============================== 37 passed in 0.03s ==============================
```

Confidence Level: ★★★★☆ (4/5)

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_task_list()` | Sorts by `HH:MM` preferred time, then priority and duration. |
| Filtering | `Scheduler.filter_tasks()`, `Owner.get_tasks_filtered()` | Filters by pet name and completion status for quick task views. |
| Conflict handling | `Scheduler.check_conflict()`, `Scheduler.detect_conflicts()` | Detects overlapping scheduled tasks and shows warnings instead of crashing. |
| Recurring tasks | `CareTask.mark_complete()`, `CareTask.create_next_occurrence()`, `Scheduler.expand_recurring_tasks()` | Recreates daily/weekly tasks with the next due date after completion. |

## Demo Walkthrough

1. Open the Streamlit app and enter the owner's availability window.
2. Add at least two pets, then add tasks to each pet from the task form.
3. Use the task explorer to view tasks sorted by time and filtered by pet or completion status.
4. Click **Generate schedule** to build a per-pet daily plan.
5. Review the schedule tables, skipped tasks, and any conflict warnings shown in yellow.
6. Check the CLI demo (`main.py`) to see the same algorithms demonstrated in the terminal.

**Screenshot or video** *(optional)*: You can add one here if you want to show the UI visually.# PawPal+ (Module 2 Project)

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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:
```
Today's Schedule:

Daily plan for Biscuit (dog):
Scheduled tasks:
	08:00 - 08:10: Feed (10 min) [priority: high]
	08:10 - 08:40: Morning walk (30 min) [priority: high]
	08:40 - 09:00: Play (20 min) [priority: medium]

----------------------------------------

Daily plan for Mochi (cat):
Scheduled tasks:
	08:00 - 08:10: Feed (10 min) [priority: high]
	08:10 - 08:15: Litter clean (5 min) [priority: medium]

----------------------------------------
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest
```

This automated suite validates core scheduler behavior, including:
- chronological sorting by task time,
- filtering by pet and completion status,
- recurring task generation after completion,
- conflict detection warnings,
- plan generation and edge cases (no tasks / constrained time windows).

Successful test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-7.4.4, pluggy-1.0.0
rootdir: /Users/tigerchandler/fellowship-readiness-tracker/ai110-module2show-pawpal-starter
plugins: anyio-4.2.0
collected 37 items

tests/test_pawpal.py .....................................               [100%]

============================== 37 passed in 0.03s ==============================
```

Confidence Level: ★★★★☆ (4/5)

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
