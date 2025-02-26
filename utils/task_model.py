import time
from typing import List

from loader import bot_base


class TaskModel:
    """Класс для реализации контейнера для "Заданий" """
    def __init__(self, channels_list: List[str], reward: int, task_id=int(time.time())):
        self.task_id = task_id  # Каждый ID это секунды создания
        self.channels_list = channels_list  # Список для каналов на которые нужно подписаться для выполнения задания
        self.reward = reward
        self.who_complete = set()  # Множество с теми, кто выполнил задание

    def __str__(self):
        chl_lst_str = '\n'.join(self.channels_list)
        who = ' '.join(self.who_complete)
        ret_str = (f'Task ID: {self.task_id}\n'
                   f'Channels: {chl_lst_str}\n'
                   f'Reward: {self.reward}\n'
                   f'Who complete: {who}')
        return ret_str

    async def new_complete(self, user_id):
        """Новый исполнитель"""
        self.who_complete.add(user_id)
        await bot_base.new_executor(self.task_id, '$'.join(self.who_complete))


class TaskList:
    """Класс для реализации интерфейса для массива "Заданий" """
    def __init__(self):
        self.content_list: List[TaskModel] = []

    async def save_new_task(self, channels_list: List[str], reward: int):
        """Сохраняем новую задачу в основной список и в базу"""
        new_task = TaskModel(channels_list, reward)
        self.content_list.append(new_task)
        await bot_base.add_new_task(new_task.task_id, '$'.join(channels_list), reward)

    async def load_task_list_from_db(self):
        """Выгружаем из базы"""

        task_from_db = await bot_base.get_all_tasks()
        for task in task_from_db:
            db_task = TaskModel(
                channels_list=task[1].split('$'),
                reward=task[2],
                task_id=task[0])

            self.content_list.append(db_task)


task_manager = TaskList()
