import time
from typing import List

from loader import bot_base


class TaskModel:
    """Класс для реализации контейнера для "Заданий" """
    def __init__(self, channels_list: List[str], reward: int):
        self.id = int(time.time())  # Каждый ID это секунды создания
        self.channels_list = channels_list  # Список для каналов на которые нужно подписаться для выполнения задания
        self.reward = reward
        self.who_complete = set()  # Множество с теми, кто выполнил задание

    async def new_complete(self, user_id):
        """Новый исполнитель"""
        self.who_complete.add(user_id)
        await bot_base.new_executor(self.id, '$'.join(self.who_complete))


class TaskList:
    """Класс для реализации интерфейса для массива "Заданий" """
    def __init__(self):
        self.content_list: List[TaskModel] = []

    async def save_new_task(self, channels_list: List[str], reward: int):
        """Сохраняем новую задачу в основной список и в базу"""
        new_task = TaskModel(channels_list, reward)
        self.content_list.append(new_task)
        await bot_base.add_new_task(new_task.id, '$'.join(channels_list), reward)


task_manager = TaskList()
