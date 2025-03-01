import time
from typing import List
import random

from aiogram.types import ChatMemberLeft

from loader import bot_base, bot


class TaskModel:
    """Класс для реализации контейнера для "Заданий" """
    def __init__(self, channels_list: List[str], reward: int, task_id: int, who_complete=None):
        self.task_id: int = task_id  # Каждый ID это секунды создания
        # Список для каналов на которые нужно подписаться для выполнения задания
        self.channels_list: List[str] = channels_list
        self.reward = reward  # Вознаграждение
        # Множество с теми, кто выполнил задание
        self.who_complete = who_complete if who_complete and '' not in who_complete else set()

    def __str__(self):
        chl_lst_str = '\n'.join(self.channels_list)
        who = '$'.join(self.who_complete)
        ret_str = (f'Task ID: {self.task_id}\n'
                   f'Channels: {chl_lst_str}\n'
                   f'Reward: {self.reward}\n'
                   f'Who complete: {who}')
        return ret_str

    async def new_complete(self, user_id):
        """Новый исполнитель"""
        self.who_complete.add(user_id)
        await bot_base.new_executor(self.task_id, '$'.join(self.who_complete))

    async def executors_list(self):
        """Возвращаем список исполнителей превращенных в int"""
        return [int(i) for i in self.who_complete]

    async def check_execute(self, user_id: int):
        """Проверяем, выполнял ли пользователь задачу"""
        return True if str(user_id) in self.who_complete else False

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

    async def task_generator(self):
        """Создаем генератор с заданиями"""
        for task in self.content_list:
            yield task

    async def check_execution(self, user_id: int, task_id: int):
        """Проверяем выполнение задания конкретным исполнителем. Считаем общее кол-во каналов и
        возвращаем список исполненных"""

        for task in self.content_list:

            channels_count = 0  # Общее кол-во каналов
            execute_channels_count = []  # Список готовых каналов

            if task_id == task.task_id:
                task_channels_list = task.channels_list

                for channel in task_channels_list:

                    if channel.startswith('https://t.me/'):
                        channels_count += 1  # Считаем общее кол-во каналов в задании
                        # Проверяем подписан ли исполнитель на канал из списка
                        is_execute = await bot.get_chat_member(
                            chat_id=channel.replace('https://t.me/', '@'),
                            user_id=user_id
                        )
                        if not isinstance(is_execute, ChatMemberLeft):  # Значит подписан
                            execute_channels_count.append(channel)

                return channels_count, execute_channels_count

    async def save_new_task(self, channels_list: List[str], reward: int):
        """Сохраняем новую задачу в основной список и в базу"""
        task_id = int(time.time())
        new_task = TaskModel(channels_list, reward, task_id)
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
                task_id=task[0],
                who_complete={i for i in task[3].split('$')} if task[3] else set())
            self.content_list.append(db_task)


task_manager = TaskList()
