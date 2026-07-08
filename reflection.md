# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- 3 core Actions:
  - View all Tasks
  - Check items off the list of tasks
  - Delete a Task

- Briefly describe your initial UML design.

```mermaid
class Owner {
    -str name
    -str available_start
    -str available_end
    -list preferences

    +set_availability()
    +update_preferences()
}

class Pet {
    -str name
    -str species
    -str breed

    +update_info()
}

class CareTask {
    -str name
    -str category
    -int duration
    -str priority
    -str preferred_time

    +update_task()
    +validate()
}

class Scheduler {
    -list tasks
    -str available_start
    -str available_end

    +sort_tasks()
    +check_conflict()
    +generate_plan()
    +assign_times()
}

class DailyPlan {
    -Pet pet
    -list scheduled_tasks
    -list skipped_tasks
    -str explanation

    +add_task()
    +skip_task()
    +explain_plan()
    +display_plan()
}
```

- What classes did you include, and what responsibilities did you assign to each?

**Owner**: Stores owner info (name, availability window, preferences) and manages pets and aggregated task access.

**Pet**: Represents a specific pet, stores its details, and owns that pet’s task list.

**CareTask**: Represents one care activity with duration, priority, optional preferred time, recurrence state, and completion tracking.

**Scheduler**: The orchestration layer that loads tasks, sorts them, filters them, expands recurring tasks, detects conflicts, and generates plans.

**DailyPlan**: Holds the final scheduled and skipped tasks for one pet and formats the explanation shown to the user.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I changed the design in a few important ways while implementing the system. I added a `ScheduledTask` class so the scheduler could represent concrete time slots instead of only raw tasks. I also expanded `CareTask` with `frequency`, `due_date`, and completion tracking so daily and weekly tasks could recur automatically. Finally, I added filtering helpers on `Owner` and conflict warnings in `Scheduler` so the UI could show smarter task views instead of just a simple list.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers preferred time, task priority, task duration, owner availability, pet ownership, and recurrence state. I treated preferred time as the strongest scheduling hint when a task has a specific `HH:MM` target, then used priority as the next tie-breaker, and duration as a final tie-breaker. This keeps the plan easy to understand while still respecting the most important user constraints.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff is that conflict detection is lightweight: it warns about overlapping scheduled blocks, but it does not try to automatically reschedule every conflict optimally. That is reasonable for this project because the goal is clarity and trustworthiness for a pet owner, not a complex optimization engine. It is easier to explain why a task was warned about and lets the user decide what to change.

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI most effectively for design brainstorming, small algorithm ideas, and test drafting. The most helpful prompts were specific ones like asking for edge cases, asking how to sort `HH:MM` strings with a lambda key, and asking how to structure recurrence logic with `timedelta`. The AI was especially useful for quickly comparing approaches, but I still reviewed the result before adopting it.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I rejected an overly clever scheduling suggestion that tried to optimize too many things at once. It was technically possible, but it would have made the system harder to read and explain. I kept the simpler first-fit conflict logic because I could verify it with tests and explain it clearly in the UI.

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested task validation, adding and removing tasks, owner filtering, time sorting, recurring task regeneration, and conflict detection. These tests were important because they proved the scheduler behaves correctly on both happy paths and edge cases such as duplicate times, no tasks, and weekly recurrence boundaries.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am highly confident in the current scheduler because the core logic is covered by automated tests and the CLI demo shows the algorithms working together. If I had more time, I would test timezone handling, longer scheduling windows, and more complex overlaps where multiple pets have many tasks at similar times.

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with how the system now feels connected end-to-end: the UML matches the backend, the backend powers the UI, and the tests prove the scheduler is not just a demo but a working system.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

In another iteration, I would add a richer scheduling model with explicit time-slot objects and maybe a better rescheduling strategy for conflicts. I would also improve the Streamlit forms so task creation and filtering feel even more polished.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The biggest takeaway is that AI is most valuable when I act as the lead architect. The AI can generate ideas quickly, but I still need to decide what fits the design, keep the system readable, and verify behavior with tests. Separate chat sessions helped me stay organized by keeping architecture, implementation, and testing discussions from blending together.

**AI strategy reflection:** The most effective AI features were rapid brainstorming, code drafting, and test idea generation. I also learned to reject suggestions that were too complex for the project’s goals. Keeping separate chat sessions for planning, implementation, and testing made it easier to focus on one concern at a time and avoid mixing design decisions with debugging. That helped me stay in control as the human lead architect while still benefiting from the speed of AI assistance.# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- 3 core Actions:
View all Tasks
Check items off the list of tasks
Delete a Task


- Briefly describe your initial UML design.
class Owner {
    -str name
    -str available_start
    -str available_end
    -list preferences

    +set_availability()
    +update_preferences()
}

class Pet {
    -str name
    -str species
    -str breed

    +update_info()
}

class Owner {
    -str name
    -str available_start
    -str available_end
    -list preferences

    +set_availability()
    +update_preferences()
}

class CareTask {
    -str name
    -str category
    -int duration
    -str priority
    -str preferred_time

    +update_task()
    +validate()
}

class Scheduler {
    -list tasks
    -str available_start
    -str available_end

    +sort_tasks()
    +check_conflict()
    +generate_plan()
    +assign_times()
}


class DailyPlan {
    -Pet pet
    -list scheduled_tasks
    -list skipped_tasks
    -str explanation

    +add_task()
    +skip_task()
    +explain_plan()
    +display_plan()
}
- What classes did you include, and what responsibilities did you assign to each?

**Owner**: Stores owner info (name, availability window as start/end times, list of preferences). Methods: `set_availability()` to update time constraints, `update_preferences()` to modify owner preferences. Acts as a primary entity that pets and tasks relate back to.

**Pet**: Represents a pet with name, species, breed, and a reference to its owner. Methods: `update_info()` to modify pet attributes. Serves as the entity that care tasks are assigned to.

**CareTask**: Represents a single care activity (e.g., walk, feeding, medicine). Attributes: name, category, duration (minutes), priority (low/medium/high), preferred_time, and pet. Methods: `update_task()` to modify task details, `validate()` to check required fields before scheduling.

**Scheduler**: The scheduling engine that takes an owner, list of pets, and list of tasks, then produces a daily plan. Methods: `sort_tasks()` to order by priority/duration, `check_conflict()` to detect overlaps, `generate_plan()` to produce the final DailyPlan, `assign_times()` to slot tasks into concrete time slots.

**DailyPlan**: A container for the final schedule for one pet. Attributes: pet, scheduled_tasks (tasks that fit), skipped_tasks (tasks that didn't fit), explanation. Methods: `add_task()`, `skip_task()`, `explain_plan()`, `display_plan()` to show the user-facing output.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

**Potential improvements identified during skeleton review:**

1. **Add ScheduledTask class** — The skeleton lacks a way to represent a task *at a specific time*. Recommend adding a `@dataclass ScheduledTask` with `task: CareTask`, `start_time: str`, and `end_time: str` so the scheduler can output concrete time assignments.

2. **Clarify Scheduler.generate_plan() return** — Currently returns one `DailyPlan`, but with multiple pets, consider returning `List[DailyPlan]` (one per pet) or a wrapper object.

3. **Use datetime.time instead of strings** — Strings like `"08:00"` are hard to do math on. Consider switching to Python `datetime.time` or integers (minutes since midnight) for easier overlap detection.

4. **Define priority sorting logic** — `sort_tasks()` doesn't specify the sort order (by priority alone? by priority + duration? by preferred_time?). The skeleton should clarify the tie-breaking rules.

5. **Add time-grid tracking to Scheduler** — To avoid conflicts, the scheduler needs to track which time slots are occupied. Consider adding a helper method or internal state to manage this.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
