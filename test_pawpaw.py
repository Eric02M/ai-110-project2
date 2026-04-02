from pawpal_system import Task, Pet, Owner, Scheduler


# --- Task Addition ---

def test_add_task_to_pet():
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Morning walk", duration_minutes=30, priority="high")
    pet.add_task(task)
    assert task in pet.tasks

def test_add_task_sets_pet_reference():
    pet = Pet(name="Luna", species="cat")
    task = Task(title="Playtime", duration_minutes=15, priority="medium")
    pet.add_task(task)
    assert task.pet is pet

def test_add_multiple_tasks_to_pet():
    pet = Pet(name="Mochi", species="dog")
    t1 = Task(title="Walk", duration_minutes=20, priority="high")
    t2 = Task(title="Feed", duration_minutes=5, priority="medium")
    pet.add_task(t1)
    pet.add_task(t2)
    assert len(pet.tasks) == 2

def test_owner_get_all_tasks_across_pets():
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    mochi.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    luna.add_task(Task(title="Litter box", duration_minutes=10, priority="high"))
    owner.add_pet(mochi)
    owner.add_pet(luna)
    assert len(owner.get_all_tasks()) == 2


# --- Task Completion ---

def test_mark_task_complete():
    task = Task(title="Feed", duration_minutes=5, priority="low")
    task.mark_complete()
    assert task.completed is True

def test_completed_task_excluded_from_pending():
    pet = Pet(name="Mochi", species="dog")
    t1 = Task(title="Walk", duration_minutes=20, priority="high")
    t2 = Task(title="Feed", duration_minutes=5, priority="low")
    pet.add_task(t1)
    pet.add_task(t2)
    t2.mark_complete()
    assert t2 not in pet.pending_tasks()
    assert t1 in pet.pending_tasks()

def test_completed_task_not_scheduled():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    t1 = Task(title="Walk", duration_minutes=20, priority="high")
    t2 = Task(title="Feed", duration_minutes=5, priority="low")
    pet.add_task(t1)
    pet.add_task(t2)
    t2.mark_complete()
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    plan = scheduler.build_plan()
    titles = [st.task.title for st in plan]
    assert "Feed" not in titles
    assert "Walk" in titles

def test_task_not_complete_by_default():
    task = Task(title="Groom", duration_minutes=10, priority="medium")
    assert task.completed is False
