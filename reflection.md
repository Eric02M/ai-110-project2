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

**Tradeoff: readability over maximum time utilization**

`build_plan()` uses a `while` loop that walks through tasks in priority order and schedules each one if it fits within the remaining time budget. The loop stops naturally when either all tasks have been checked or time runs out.

This means a large task could "use up" the budget even if a smaller, lower-priority task could have filled the remaining minutes more efficiently. The scheduler does not search for the best combination of tasks to fill time — it just takes the highest-priority ones that fit, in order.

**tradeoff:** Pet care is driven by urgency and importance, not by squeezing every minute of the day. A vet-prescribed medication should always run before a grooming session, regardless of whether swapping them would "use time better." The `while` loop makes that priority logic easy to read and trace, which matters more here than optimal time packing.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools were used across every phase of this project:

- **Design brainstorming** — Used Claude to review the initial UML and identify gaps, such as the missing back-reference from `Task` to `Pet` and the redundancy between `Scheduler.time_budget` and `Owner.available_minutes`.
- **Code generation** — Generated class skeletons from the UML, then iteratively added logic for recurring tasks, conflict detection, and the while-loop scheduler.
- **Refactoring** — Asked Copilot to review `build_plan()` for readability. It suggested switching from a `for` loop with `break`/`continue` to a `while` loop with named boolean guards (`fits_in_budget`, `no_conflict`), which made the conditions self-documenting.
- **Debugging** — Pasted test failures into chat to diagnose why conflict detection never fired inside `build_plan()`. The AI identified that sequential slot assignment meant `_would_conflict()` was a defensive guard rather than an active one.
- **Test generation** — Used AI to generate comprehensive test cases across 7 areas, then asked it to annotate each test with `# Test:` and `# Expected:` comments so the intent was always visible.

The most helpful prompts were specific and architectural: *"Why would `_would_conflict()` never fire with the current design?"* produced a more useful answer than *"fix my conflict detection."*

**b. Judgment and verification**

When asked to simplify `build_plan()` for readability, the AI initially suggested a `for` loop with an explicit `break` when time ran out. This would have silently skipped lower-priority tasks that could still fit after a large task was rejected. I rejected this approach because it changed the scheduling behavior, not just the style — the `while` loop with `index += 1` continuing past skipped tasks was the correct semantics.

I verified by tracing through a scenario with a high-priority 60-minute task and two low-priority 10-minute tasks against a 70-minute budget. The `for`+`break` version would have stopped after the 60-minute task and skipped both 10-minute tasks even though one would fit. The `while` version correctly continued evaluating and scheduled one of them.

---

## 3b. AI Strategy — VS Code Copilot

**Which Copilot features were most effective for building your scheduler?**

The inline autocomplete was most useful during repetitive structural work — filling out `__str__` methods, dataclass field declarations, and pytest fixtures. It correctly inferred patterns from the first few classes and reproduced them consistently.

The chat panel was more valuable for architectural questions. Asking *"How could this algorithm be simplified for better readability or performance?"* on `build_plan()` produced the named-boolean refactor (`fits_in_budget`, `no_conflict`) that made the while-loop guards readable without changing behavior.

**One AI suggestion I rejected or modified:**

Copilot suggested adding a `break` inside the while loop when a task exceeded the budget, treating the first over-budget task as a stopping condition. I modified this because the tasks are sorted by priority — a high-priority 90-minute task could be rejected while a low-priority 5-minute task could still fit. Breaking early would produce an incomplete plan. The fix was to continue the loop past rejected tasks using `index += 1` unconditionally, only stopping when the budget was fully exhausted or all tasks were evaluated.

**How did using separate chat sessions for different phases help?**

Keeping design, implementation, and testing in separate sessions prevented earlier context from biasing later decisions. The design session focused purely on class responsibilities and relationships without implementation details bleeding in. The testing session started from the finished code and could ask "what could go wrong?" without being anchored to how the code was written. Mixing all phases into one session tends to produce solutions that defend the existing code rather than stress-testing it.

**What I learned about being the "lead architect" when collaborating with AI:**

The AI is a fast, capable executor but has no stake in correctness or coherence. It will generate plausible-sounding code that subtly changes behavior, introduces redundancy, or optimizes for the wrong thing — and it will do so confidently. The lead architect's job is to define *what the system should do* before asking AI to help build it, and to verify that every suggestion preserves that intent. Accepting a suggestion without tracing through a concrete example is the most common way to introduce bugs. The AI accelerates implementation significantly, but judgment about what to build and whether it is correct remains entirely with the developer.

---

## 4. Testing and Verification

**a. What you tested**

36 tests across 7 areas:

- **Task addition** — Tasks are stored in the pet and the back-reference to `pet` is set correctly.
- **Task completion** — `mark_complete()` sets the flag; completed tasks are excluded from pending lists and from the scheduled plan.
- **Priority sorting** — High priority is always scheduled before medium; shorter tasks win tiebreakers; `get_priority_score()` returns correct values.
- **Time budget** — Exact-fit tasks are scheduled; tasks one minute over budget are skipped; zero budget and empty task lists produce no crashes.
- **Recurring tasks** — `"once"` produces no next task; `"daily"` advances by 1 day; `"weekly"` advances by 7 days; next task is auto-registered with the pet.
- **Filter and sort** — `filter_tasks` by completion and pet name; `sort_by_time` returns ascending order.
- **Conflict detection** — Normal plans have no conflicts; overlapping slots injected directly are flagged; back-to-back slots are not flagged.

These tests mattered because the scheduler's correctness depends on the interaction between multiple classes. A bug in `Pet.add_task` would silently break `Scheduler.build_plan`. Testing each layer in isolation makes failures easy to locate.

**b. Confidence**

★★★★☆ (4 / 5)

All 36 tests pass. Core behaviors are well covered. The one gap is that `_would_conflict()` inside `build_plan()` can never actually fire under the current sequential design — tasks are assigned start times immediately after the previous task ends, so no overlap is geometrically possible. The guard is correct but untested against a real runtime conflict. Confidence would reach 5 stars if tasks supported fixed start times and a genuine scheduling conflict could be triggered end-to-end.

---

## 5. Reflection

**a. What went well**

The while-loop design for `build_plan()` is the part of this project I am most satisfied with. It reads almost like a plain English description of the scheduling rule: *while there is time and tasks remaining, take the next task if it fits.* The named boolean variables make the two conditions explicit without requiring comments. The algorithm is easy to trace, easy to test, and easy to extend.

**b. What you would improve**

The biggest gap is that tasks have no fixed start time. Every task is scheduled sequentially from minute 0, which means the conflict detection guard inside `build_plan()` is defensive code that can never fire. In a real pet care app, some tasks have hard time constraints — a vet appointment at 2pm, medication at 8am and 8pm. The next iteration would add an optional `fixed_start: int | None` field to `Task` and update `build_plan()` to place fixed-time tasks first, then fill remaining slots with flexible tasks. That change would also make `_would_conflict()` genuinely necessary.

**c. Key takeaway**

Designing the system before writing code made the AI collaboration substantially more productive. When the class responsibilities were defined in the UML first, every AI prompt had a clear frame: *"Here is what this method is supposed to do — help me implement it."* Without that frame, AI tends to generate working code that solves a slightly different problem. The most important skill in AI-assisted development is not prompting — it is knowing what you want clearly enough to recognize when the AI has drifted from it.
