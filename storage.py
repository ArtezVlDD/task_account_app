# storage.py
import json
import os
from models import Task


class Storage:
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = []
        self.load()

    def load(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            self.tasks = []

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([t.to_dict() for t in self.tasks], f, ensure_ascii=False, indent=2)
            return True
        except:
            return False

    def get_next_id(self):
        """Находит первый свободный ID (переиспользуем удаленные)"""
        if not self.tasks:
            return 1

        existing_ids = sorted([t.id for t in self.tasks])

        # Ищем пропуск в нумерации
        for i, tid in enumerate(existing_ids, start=1):
            if tid != i:
                return i

        return len(existing_ids) + 1

    def find_by_id(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def add(self, task):
        self.tasks.append(task)
        return self.save()

    def update(self, task_id, **kwargs):
        task = self.find_by_id(task_id)
        if not task:
            return False

        if "title" in kwargs and kwargs["title"]:
            task.title = kwargs["title"].strip()
        if "description" in kwargs:
            task.description = kwargs["description"].strip()
        if "responsible" in kwargs and kwargs["responsible"]:
            task.responsible = kwargs["responsible"].strip()
        if "status" in kwargs and kwargs["status"] in Task.STATUSES:
            task.status = kwargs["status"]
        if "deadline" in kwargs and kwargs["deadline"]:
            task.deadline = kwargs["deadline"]

        return self.save()

    def delete(self, task_id):
        task = self.find_by_id(task_id)
        if task:
            self.tasks.remove(task)
            return self.save()
        return False

    def get_all(self):
        return self.tasks.copy()