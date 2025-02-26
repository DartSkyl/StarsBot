import time
from typing import List

from loader import bot_base


class TaskModel:
    """Класс для реализации контейнера для "Заданий" """
    def __init__(self, channels_list: List[str]):
        self.id = int(time.time())  # Каждый ID это секунды создания
        self.channels_list = channels_list  # Список для каналов на которые нужно подписаться для выполнения задания
        self.who_complete = set()  # Множество с теми, кто выполнил задание


class TaskList:
    """Класс для реализации интерфейса для массива "Заданий" """
    def __init__(self):
        self.content_list: List[TaskModel] = []

    async def save_new_task(self, channels_list: List[str]):
        """Сохраняем новую задачу в основной список и в базу"""
        new_task = TaskModel(channels_list)
        self.content_list.append(new_task)
        await bot_base.add_new_task(new_task.id, '$'.join(channels_list))

