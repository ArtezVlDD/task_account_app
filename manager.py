# manager.py
from datetime import datetime
from models import Task
from storage import Storage


class TaskManager:
    def __init__(self, username=None):
        self.storage = Storage()
        self.username = username

    def _can_access(self, task):
        """Проверка доступа к задаче"""
        if not self.username or self.username == "admin":
            return True
        return task.responsible == self.username

    def _filter_by_user(self, tasks):
        """Фильтр задач по пользователю"""
        if not self.username or self.username == "admin":
            return tasks
        return [t for t in tasks if t.responsible == self.username]

    def add_task(self, title, description, responsible, deadline):
        # Валидация
        if not title or not title.strip():
            return False, "Название не может быть пустым"

        try:
            datetime.strptime(deadline, Task.DATE_FORMAT)
        except:
            return False, f"Неверный формат даты. Нужно: {Task.DATE_FORMAT}"

        # Если не админ и ответственный не указан - ставим текущего
        if self.username and self.username != "admin" and not responsible:
            responsible = self.username

        if not responsible:
            return False, "Укажите ответственного"

        task_id = self.storage.get_next_id()
        task = Task(task_id, title, description, responsible, deadline)

        if self.storage.add(task):
            return True, task
        return False, "Ошибка сохранения"

    def get_all_tasks(self):
        return self._filter_by_user(self.storage.get_all())

    def get_by_status(self, status):
        if status not in Task.STATUSES:
            return []
        all_tasks = self._filter_by_user(self.storage.get_all())
        return [t for t in all_tasks if t.status == status]

    def get_by_responsible(self, name):
        all_tasks = self._filter_by_user(self.storage.get_all())
        return [t for t in all_tasks if name.lower() in t.responsible.lower()]

    def get_overdue(self):
        all_tasks = self._filter_by_user(self.storage.get_all())
        return [t for t in all_tasks if t.is_overdue()]

    def update_task(self, task_id, **kwargs):
        task = self.storage.find_by_id(task_id)
        if not task:
            return False, f"Задача {task_id} не найдена"

        if not self._can_access(task):
            return False, "Нет доступа к этой задаче"

        if "deadline" in kwargs and kwargs["deadline"]:
            try:
                datetime.strptime(kwargs["deadline"], Task.DATE_FORMAT)
            except:
                return False, f"Неверный формат даты"

        if self.storage.update(task_id, **kwargs):
            return True, "Задача обновлена"
        return False, "Ошибка обновления"

    def mark_done(self, task_id):
        task = self.storage.find_by_id(task_id)
        if not task:
            return False, f"Задача {task_id} не найдена"

        if not self._can_access(task):
            return False, "Нет доступа"

        if task.status == "выполнена":
            return False, "Задача уже выполнена"

        if self.storage.update(task_id, status="выполнена"):
            return True, f"Задача {task_id} выполнена"
        return False, "Ошибка"

    def delete_task(self, task_id):
        task = self.storage.find_by_id(task_id)
        if not task:
            return False, f"Задача {task_id} не найдена"

        if not self._can_access(task):
            return False, "Нет доступа"

        if self.storage.delete(task_id):
            return True, f"Задача {task_id} удалена"
        return False, "Ошибка"