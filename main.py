# main.py
from datetime import datetime
from models import Task
from manager import TaskManager
import storage


def print_table(tasks):
    """Вывод таблицы задач"""
    if not tasks:
        print("\nНет задач\n")
        return

    tasks = sorted(tasks, key=lambda x: x.id)

    print("\n" + "=" * 95)
    print(f"{'ID':>4} | {'Название':<30} | {'Ответственный':<20} | {'Статус':<12} | {'Дедлайн':<10}")
    print("-" * 95)

    for t in tasks:
        mark = "!" if t.is_overdue() else " "
        print(f"{mark}{t.id:>3} | {t.title[:29]:<30} | {t.responsible[:19]:<20} | {t.status:<12} | {t.deadline:<10}")

    print("=" * 95)
    print(f"Всего: {len(tasks)}\n")


def show_help():
    print("""
КОМАНДЫ:
  add                           - Добавить задачу
  list                          - Показать все задачи
  show [новая|в работе|выполнена] - Задачи по статусу
  update [id]                   - Изменить задачу
  done [id]                     - Отметить как выполненную
  delete [id]                   - Удалить задачу
  responsible [имя]             - Задачи сотрудника
  overdue                       - Просроченные задачи
  export                        - Экспорт в CSV
  help                          - Справка
  exit                          - Выход
""")


def export_csv(tasks):
    import csv
    if not tasks:
        print("\nНет задач для экспорта\n")
        return

    filename = f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Название", "Описание", "Ответственный", "Статус", "Создана", "Дедлайн"])
            for t in tasks:
                writer.writerow([t.id, t.title, t.description, t.responsible, t.status, t.created_at, t.deadline])

        print(f"\nЭкспортировано в {filename}\n")
    except Exception as e:
        print(f"\nОшибка экспорта: {e}\n")


def main():
    print("\n" + "=" * 50)
    print("  УЧЕТ ЗАДАЧ - Строительная фирма")
    print("=" * 50)

    # Авторизация
    username = input("\nВаше имя (или 'admin'): ").strip()
    if not username:
        username = "guest"

    manager = TaskManager(username if username != "admin" else None)

    if username == "admin":
        print("\nРежим: АДМИНИСТРАТОР (все задачи)")
    else:
        print(f"\nРежим: {username} (только свои задачи)")

    # Проверка просрочек при старте
    overdue = manager.get_overdue()
    if overdue:
        print(f"\nВНИМАНИЕ! {len(overdue)} просроченных задач:")
        print_table(overdue)

    show_help()

    while True:
        try:
            cmd = input("\n> ").strip().lower()

            if cmd == "exit":
                print("\nДо свидания!")
                break

            elif cmd == "help":
                show_help()

            elif cmd == "list":
                print_table(manager.get_all_tasks())

            elif cmd == "add":
                print("\n--- Новая задача ---")

                title = input("Название: ").strip()
                if not title:
                    print("Ошибка: нужно название")
                    continue

                description = input("Описание: ").strip()

                if username == "admin":
                    responsible = input("Ответственный: ").strip()
                    if not responsible:
                        print("Ошибка: нужен ответственный")
                        continue
                else:
                    responsible = username
                    print(f"Ответственный: {responsible}")

                while True:
                    deadline = input(f"Срок ({Task.DATE_FORMAT}): ").strip()
                    if deadline:
                        try:
                            datetime.strptime(deadline, Task.DATE_FORMAT)
                            break
                        except:
                            print(f"Неверный формат! Пример: {Task.DATE_FORMAT}")
                    else:
                        print("Дедлайн обязателен")

                ok, result = manager.add_task(title, description, responsible, deadline)
                if ok:
                    print(f"\nЗадача #{result.id} добавлена")
                else:
                    print(f"\nОшибка: {result}")

            elif cmd.startswith("show "):
                status = cmd[5:].strip()
                if status not in Task.STATUSES:
                    print(f"Неверный статус. Доступны: {', '.join(Task.STATUSES)}")
                else:
                    print_table(manager.get_by_status(status))

            elif cmd.startswith("update "):
                try:
                    task_id = int(cmd[7:].strip())
                except:
                    print("ID должен быть числом")
                    continue

                task = manager.storage.find_by_id(task_id)
                if not task:
                    print(f"Задача {task_id} не найдена")
                    continue

                if not manager._can_access(task):
                    print("Нет доступа")
                    continue

                print(f"\n--- Редактирование #{task_id} ---")
                print(f"Название [{task.title}]: ", end="")
                new_title = input().strip()

                print(f"Описание [{task.description}]: ", end="")
                new_desc = input().strip()

                if username == "admin":
                    print(f"Ответственный [{task.responsible}]: ", end="")
                    new_resp = input().strip()
                else:
                    new_resp = None

                print(f"Статус [{task.status}] (новая/в работе/выполнена): ", end="")
                new_status = input().strip().lower()
                if new_status and new_status not in Task.STATUSES:
                    print(f"Статус '{new_status}' не существует")
                    new_status = None

                print(f"Дедлайн [{task.deadline}]: ", end="")
                new_deadline = input().strip()
                if new_deadline:
                    try:
                        datetime.strptime(new_deadline, Task.DATE_FORMAT)
                    except:
                        print("Неверный формат, дедлайн не изменен")
                        new_deadline = None

                updates = {}
                if new_title:
                    updates["title"] = new_title
                if new_desc:
                    updates["description"] = new_desc
                if new_resp:
                    updates["responsible"] = new_resp
                if new_status:
                    updates["status"] = new_status
                if new_deadline:
                    updates["deadline"] = new_deadline

                if updates:
                    ok, msg = manager.update_task(task_id, **updates)
                    print(f"\n{'OK' if ok else 'Ошибка'}: {msg}")
                else:
                    print("\nНет изменений")

            elif cmd.startswith("done "):
                try:
                    task_id = int(cmd[5:].strip())
                except:
                    print("ID должен быть числом")
                    continue

                ok, msg = manager.mark_done(task_id)
                print(f"\n{'OK' if ok else 'Ошибка'}: {msg}")

            elif cmd.startswith("delete "):
                try:
                    task_id = int(cmd[7:].strip())
                except:
                    print("ID должен быть числом")
                    continue

                confirm = input(f"Удалить задачу {task_id}? (y/N): ").strip().lower()
                if confirm == 'y':
                    ok, msg = manager.delete_task(task_id)
                    print(f"\n{'OK' if ok else 'Ошибка'}: {msg}")

            elif cmd.startswith("responsible "):
                name = cmd[11:].strip()
                if not name:
                    print("Укажите имя")
                else:
                    print_table(manager.get_by_responsible(name))

            elif cmd == "overdue":
                print_table(manager.get_overdue())

            elif cmd == "export":
                export_csv(manager.get_all_tasks())

            else:
                print(f"Неизвестно: {cmd}. Введите 'help'")

        except KeyboardInterrupt:
            print("\n\nВыход...")
            break
        except Exception as e:
            print(f"\nОшибка: {e}\n")


if __name__ == "__main__":
    main()