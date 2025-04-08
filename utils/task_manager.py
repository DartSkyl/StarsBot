import time
from typing import List
from random import choices
import string

from aiogram.types import ChatMemberLeft
from aiogram.exceptions import TelegramBadRequest

from loader import bot_base, bot


class TaskModel:
    """Класс для реализации контейнера для "Заданий" """

    # def __init__(self, channels_list: List[str], reward: int, task_id: int, complete_count: int, who_complete=None):
    #     self.task_id: int = task_id  # Каждый ID это секунды создания
    #     # Список для каналов на которые нужно подписаться для выполнения задания
    #     self.channels_list: List[str] = channels_list
    #     self.reward: int = reward  # Вознаграждение
    #     self.complete_count: int = complete_count
    #     # Множество с теми, кто выполнил задание
    #     self.who_complete: set = who_complete if who_complete and '' not in who_complete else set()

    def __init__(
            self,
            task_id: str,
            task_name: str,
            serial_number: int,
            channel: str,
            channel_id: int,
            reward: int,
            complete_count: int,
            who_complete=None
    ):

        self.task_id: str = task_id  # Случайная строка и букв и цифр
        self.task_name: str = task_name
        self.serial_number: int = serial_number
        self.channel: str = channel  # В каждом задании только один канал
        self.channel_id = channel_id  # Если канал закрытый, то нужен его ID. Если ID 0, то канал открытый
        self.reward: int = reward  # Вознаграждение
        self.complete_count: int = complete_count
        # Множество с теми, кто выполнил задание
        self.who_complete: set = who_complete if who_complete and '' not in who_complete else set()

    def __str__(self):
        who = '$'.join(self.who_complete)
        ret_str = (f'Task ID: {self.task_id}\n'
                   f'Task name: {self.task_name}\n'
                   f'Serial number: {self.serial_number}\n'
                   f'Channel: {self.channel}\n'
                   f'Channel ID: {self.channel_id}\n'
                   f'Reward: {self.reward}\n'
                   f'Complete count: {self.complete_count}\n'
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

    async def check_complete_count(self):

        return len(self.who_complete) >= self.complete_count

    async def edit_task(
            self,
            new_channel: str = None,
            new_channel_id: int = None,
            new_task_name: str = None,
            reward: int = None,
            complete_count: int = None
    ):
        """Изменяем задание"""
        if new_channel:
            self.channel = new_channel
            await bot_base.edit_task_channel(task_id=self.task_id, new_channel=new_channel)
        elif new_channel_id:
            self.channel_id = new_channel_id
            await bot_base.edit_task_channel_id(task_id=self.task_id, new_channel_id=new_channel_id)
        elif new_task_name:
            self.task_name = new_task_name
            await bot_base.new_task_name(task_id=self.task_id, new_task_name=new_task_name)
        elif reward:
            self.reward = reward
            await bot_base.edit_task_reward(task_id=self.task_id, reward=reward)
        elif complete_count:
            self.complete_count = complete_count
            await bot_base.edit_task_complete_count(task_id=self.task_id, complete_count=complete_count)


class TaskList:
    """Класс для реализации интерфейса для массива "Заданий" """

    def __init__(self):
        self.content_list: List[TaskModel] = []

    async def get_tasks_list(self):
        """Возвращаем список текущих заданий"""
        return self.content_list

    async def get_task_by_id(self, task_id: int):
        """Возвращаем конкретное задание по ID"""
        for task in self.content_list:
            if task_id == task.task_id:
                return task

    async def get_task_by_serial_number(self, serial_number: int):
        """Возвращаем конкретное задание по порядковому номеру"""
        for task in self.content_list:
            if serial_number == task.serial_number:
                return task

    async def task_generator(self):
        """Создаем генератор с заданиями"""
        for task in self.content_list:
            yield task

    async def check_execution(self, user_id: int, task_id: int):
        """Проверяем выполнение задания конкретным исполнителем."""
        for task in self.content_list:
            if task_id == task.task_id:
                try:
                    if task.channel != 'https://t.me/CyberLaboratory_Bot':
                        if not task.channel.startswith('https://t.me/+'):
                            channel = task.channel.replace('https://t.me/', '@')
                        else:
                            channel = task.channel_id
                        is_execute = await bot.get_chat_member(
                            chat_id=channel,
                            user_id=user_id
                        )
                        print(type(is_execute))
                        if not isinstance(is_execute, ChatMemberLeft):  # Значит подписан
                            return True
                        return False
                    else:
                        return await bot_base.check_task_complete(user_id)
                except TelegramBadRequest as e:
                    print(e)
                    print(task.channel_id)
                    print()

    async def save_new_task(
            self,
            task_name: str,
            serial_number: int,
            channel: str,
            channel_id: int,
            reward: int,
            complete_count: int
    ):
        """Сохраняем новую задачу в основной список и в базу"""
        task_id = ''.join(choices(string.digits + string.ascii_letters, k=8))

        new_task = TaskModel(
            task_id=task_id,
            task_name=task_name,
            serial_number=serial_number,
            channel=channel,
            channel_id=channel_id,
            reward=reward,
            complete_count=complete_count
        )

        await bot_base.add_new_task(
            task_id=new_task.task_id,
            task_name=task_name,
            serial_number=serial_number,
            channel=channel,
            channel_id=channel_id,
            reward=reward,
            complete_count=complete_count
        )

        self.content_list.append(new_task)

    async def edit_task(
            self,
            task_id,
            new_channel=None,
            new_channel_id=None,
            new_task_name=None,
            new_reward=None,
            complete_count=None
    ):
        """Изменяем конкретное задание"""
        for task in self.content_list:
            if task_id == task.task_id:
                if new_channel:
                    await task.edit_task(new_channel=new_channel)
                elif new_channel_id:
                    await task.edit_task(new_channel_id=new_channel_id)
                elif new_task_name:
                    await task.edit_task(new_task_name=new_task_name)
                elif new_reward:
                    await task.edit_task(reward=new_reward)
                elif complete_count:
                    await task.edit_task(complete_count=complete_count)
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
                task_id=task[0],
                task_name=task[1],
                serial_number=task[7],
                channel=task[2],
                channel_id=task[3],
                reward=task[4],
                who_complete={i for i in task[5].split('$')} if task[5] else set(),
                complete_count=task[6])
            self.content_list.append(db_task)


task_manager = TaskList()
