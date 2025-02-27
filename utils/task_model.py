import time
from typing import List

from loader import bot_base


class TaskModel:
    """Класс для реализации контейнера для "Заданий" """
    def __init__(self, channels_list: List[str], reward: int, task_id=int(time.time())):
        self.task_id: int = task_id  # Каждый ID это секунды создания
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

    async def edit_task(self, new_channels: List[str] = None, reward: int = None):
        """Изменяем задание"""
        if new_channels:
            self.channels_list = new_channels
            await bot_base.edit_task_channels(task_id=self.task_id, new_channels='$'.join(new_channels))
        elif reward:
            self.reward = reward
            await bot_base.edit_task_reward(task_id=self.task_id, reward=reward)


class TaskList:
    """Класс для реализации интерфейса для массива "Заданий" """
    def __init__(self):
        self.content_list: List[TaskModel] = []

    async def get_tasks_list(self):
        """Возвращаем список текущих заданий"""
        return self.content_list

    async def get_task(self, task_id: int):
        """Возвращаем конкретное задание"""
        for task in self.content_list:
            if task_id == task.task_id:
                return task

    async def save_new_task(self, channels_list: List[str], reward: int):
        """Сохраняем новую задачу в основной список и в базу"""
        new_task = TaskModel(channels_list, reward)
        self.content_list.append(new_task)
        await bot_base.add_new_task(new_task.task_id, '$'.join(channels_list), reward)

    async def edit_task(self, task_id, new_channels=None, new_reward=None):
        """Изменяем конкретное задание"""
        for task in self.content_list:
            if task_id == task.task_id:
                if new_channels:
                    await task.edit_task(new_channels=new_channels)
                elif new_reward:
                    await task.edit_task(reward=new_reward)
                return task

    async def remove_task(self, task_id):
        """Удаляем задание"""
        for task in self.content_list:
            if task_id == task.task_id:
                await bot_base.delete_task(task_id)
                self.content_list.remove(task)
                break

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
