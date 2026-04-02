# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- three core actions
 - task
 - pet
 - manage pet care tasks

**b. Design changes** 
1. Pet - store and manage pet information
Attributes:
* name
* age
* breed
* weight
* medical_info
Methods:
* update_info()
* display_info()

2. Task - represents care activities

Attributes:
* task_type (feeding, grooming, walking)
* time
* status (pending/completed)
* pet (reference to Pet)
Methods:
* mark_complete()
* schedule()
* reschedule()

3. Schedule / Reminder System - assigns time
Attributes:
* list_of_tasks
* date
* notifications
Methods:
* get_today_tasks()
* send_reminder()
* add_task()


- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

**Changes made based on AI skeleton review:**

1. **Added `pet: Pet | None` to `Task`** — The original design had no way to know which pet a task belonged to once tasks were flattened for scheduling. With multiple pets, the schedule output was ambiguous. Adding a back-reference to `Pet` fixes this.

2. **Typed `Pet.tasks` as `list[Task]`** — The original used a bare `list`, which gives no type safety. Changed to `list[Task]` so tools and future code know what's in the list.

3. **Added `Owner.get_all_tasks() -> list[Task]`** — The `Scheduler` needs to collect tasks across all of an owner's pets. Without this method, that traversal logic would have to live inside `Scheduler`, mixing concerns. A dedicated helper on `Owner` is cleaner.

4. **Removed `time_budget` parameter from `Scheduler.__init__`** — `Owner.available_minutes` and `Scheduler.time_budget` were redundant. Now `Scheduler` derives `time_budget` directly from `owner.available_minutes`, eliminating the risk of them getting out of sync.

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
