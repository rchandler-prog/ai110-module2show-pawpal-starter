# PawPal+ Project Reflection

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
