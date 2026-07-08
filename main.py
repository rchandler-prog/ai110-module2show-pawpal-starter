from pawpal_system import Owner, Pet, CareTask, Scheduler


def main():
    owner = Owner(name="Jordan", available_start="08:00", available_end="11:00")

    # Create pets
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever")
    mochi = Pet(name="Mochi", species="cat", breed="Siamese")

    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Add tasks out of order by preferred_time
    biscuit.add_task(
        CareTask(
            name="Morning walk",
            duration=30,
            priority="high",
            preferred_time="08:30",
            frequency="daily",
        )
    )
    biscuit.add_task(
        CareTask(
            name="Feed",
            duration=10,
            priority="high",
            preferred_time="08:00",
            frequency="daily",
        )
    )
    biscuit.add_task(
        CareTask(
            name="Play",
            duration=20,
            priority="medium",
            preferred_time="09:30",
        )
    )

    # Intentional conflict on preferred time across pets
    mochi.add_task(
        CareTask(
            name="Feed",
            duration=10,
            priority="high",
            preferred_time="08:00",
            frequency="daily",
        )
    )
    mochi.add_task(
        CareTask(
            name="Litter clean",
            duration=15,
            priority="medium",
            preferred_time="08:05",
            frequency="weekly",
        )
    )

    scheduler = Scheduler(owner)

    print("SORTED TASKS FOR BISCUIT (by preferred time):")
    sorted_biscuit_tasks = scheduler.sort_by_time(biscuit.get_tasks())
    for task in sorted_biscuit_tasks:
        print(f"- {task.preferred_time or 'None'} | {task.name} | {task.priority}")
    print()

    print("FILTERED TASKS (Biscuit + incomplete):")
    filtered = scheduler.filter_tasks(owner.get_all_tasks(), pet_name="Biscuit", completed=False)
    for task in filtered:
        print(f"- {task.name} (completed={task.completed})")
    print()

    print("RECURRING TASK AUTOMATION:")
    biscuit.mark_task_complete("Morning walk", on_date="2026-07-07")
    for task in biscuit.get_tasks():
        if task.name == "Morning walk":
            print(
                f"- {task.name}: completed={task.completed}, due_date={task.due_date}, frequency={task.frequency}"
            )
    print()

    # Generate schedule for a fixed date to demonstrate recurring due logic
    plans = scheduler.generate_plan(date_str="2026-07-07")

    print("Today's Schedule:\n")
    for plan in plans:
        print(plan.display_plan())
        print("\n" + ("-" * 40) + "\n")

    print("CONFLICT WARNINGS:")
    warnings = scheduler.detect_conflicts(plans)
    if warnings:
        for warning in warnings:
            print(f"! {warning}")
    else:
        print("No conflicts detected.")

if __name__ == "__main__":
    main()
