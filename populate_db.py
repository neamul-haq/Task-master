# populate_db.py
import os
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_management.settings")
django.setup()

from django.contrib.auth.models import User
from tasks.models import Project, Task, TaskDetail

def populate_db():
    fake = Faker()

    # Create Users
    users = []
    for _ in range(10):
        username = fake.unique.user_name()
        email = fake.unique.email()
        user = User.objects.create_user(
            username=username,
            email=email,
            password='Test@1234',
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )
        users.append(user)
    print(f"✅ Created {len(users)} users")

    # Create Projects
    projects = []
    for _ in range(5):
        project = Project.objects.create(
            name=fake.bs().title(),
            description=fake.paragraph(),
            start_date=fake.date_this_year()
        )
        projects.append(project)
    print(f"✅ Created {len(projects)} projects")

    # Create Tasks
    tasks = []
    for _ in range(20):
        task = Task.objects.create(
            project=random.choice(projects),
            title=fake.sentence(nb_words=6),
            description=fake.text(max_nb_chars=200),
            due_date=fake.date_between(start_date='today', end_date='+60d'),
            status=random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED']),
        )
        assigned_users = random.sample(users, k=random.randint(1, 3))
        task.assigned_to.set(assigned_users)
        tasks.append(task)
    print(f"✅ Created {len(tasks)} tasks")

    # Create TaskDetails
    priorities = ['H', 'M', 'L']
    for task in tasks:
        TaskDetail.objects.create(
            task=task,
            priority=random.choice(priorities),
            notes=fake.paragraph()
        )
    print("✅ Populated TaskDetails for all tasks")

    print("\n🎉 Database populated successfully!")

if __name__ == "__main__":
    populate_db()
