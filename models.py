# models.py
from datetime import datetime


class Task:
    """Модель задачи"""

    DATE_FORMAT = "%d-%m-%Y"
    STATUSES = ["новая", "в работе", "выполнена"]

    def __init__(self, id, title, description, responsible, deadline, created_at=None, status="новая"):
        self.id = id
        self.title = title.strip()
        self.description = description.strip() if description else ""
        self.responsible = responsible.strip()
        self.deadline = deadline
        self.created_at = created_at or datetime.now().strftime(self.DATE_FORMAT)
        self.status = status if status in self.STATUSES else "новая"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "responsible": self.responsible,
            "deadline": self.deadline,
            "created_at": self.created_at,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            responsible=data["responsible"],
            deadline=data["deadline"],
            created_at=data.get("created_at"),
            status=data.get("status", "новая")
        )

    def is_overdue(self):
        if self.status == "выполнена":
            return False
        try:
            deadline_date = datetime.strptime(self.deadline, self.DATE_FORMAT).date()
            return deadline_date < datetime.now().date()
        except:
            return False