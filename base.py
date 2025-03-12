import sqlite3
import datetime


async def date_string_to_epoch(date_string):
    dt = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    epoch_seconds = int(dt.timestamp())
    return epoch_seconds


class BotBase:
    """Класс для реализации базы данных и методов для взаимодействия с ней"""

    @staticmethod
    async def check_db_structure():
        """Создаем при первом подключении, а в последующем проверяем, таблицы необходимые для работы бота"""
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()

            # Таблица со всеми пользователями
            cursor.execute('CREATE TABLE IF NOT EXISTS all_users ('
                           'user_id INTEGER PRIMARY KEY,'
                           'stars INT DEFAULT 100,'  # Всегда делить на 100
                           'referer INTEGER DEFAULT 0,'  # Будем записывать каждому того, кто его привел
                           'referral_count INTEGER DEFAULT 0,'
                           'captcha VARCHAR(155) DEFAULT "False",'
                           'last_task VARCHAR(155) DEFAULT "empty",'  # Когда последний раз выполнял задание
                           'last_ref VARCHAR(155) DEFAULT "empty",'  # Когда привел последнего реферала
                           'last_bonus VARCHAR(155) DEFAULT "empty",'  # Когда активировал бонус
                           'bonus INTEGER DEFAULT 1,'
                           'username VARCHAR(155));')  # Кол-во бонусов подряд, "n"

            # Таблица с заданиями
            cursor.execute('CREATE TABLE IF NOT EXISTS tasks_list ('
                           'task_id VARCHAR(155) PRIMARY KEY, '
                           'task_name TEXT, '
                           'channel TEXT, '
                           'channel_id INTEGER, '
                           'reward INT,  '  # Всегда делить на 100
                           'who_complete TEXT, '
                           'complete_count INTEGER, '
                           'serial_number INTEGER UNIQUE'
                           ');')

            # Таблица с настройками
            cursor.execute('CREATE TABLE IF NOT EXISTS settings ('
                           'set_name VARCHAR(155) PRIMARY KEY, '
                           'set_content TEXT'
                           ');')

            # Таблица с заявками на вывод звезд
            cursor.execute('CREATE TABLE IF NOT EXISTS stars_withdrawal ('
                           'user_id INTEGER,'
                           'username VARCHAR(155) PRIMARY KEY, '
                           'requirement_stars INTEGER'
                           ');')

            # Таблица со статистикой
            cursor.execute('CREATE TABLE IF NOT EXISTS statistic ('
                           'date_int INTEGER PRIMARY KEY,'
                           'task_count INTEGER DEFAULT 0, '
                           'stars_count INTEGER DEFAULT 0'
                           ');')

            connection.commit()

    # ====================
    # Пользователи
    # ====================

    @staticmethod
    async def add_new_user(user_id, referer_id, username):
        """Вставляем сразу все столбцы"""
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()

            cursor.execute(f'INSERT INTO all_users (user_id, referer, username) '
                           f'VALUES ({user_id}, {referer_id}, "{username}")')

            # И сразу посчитаем рефереру его сучку
            cursor.execute(f"UPDATE all_users "
                           f"SET referral_count = referral_count + 1 "
                           f"WHERE user_id = {referer_id};")

            # И обновим last_ref реферера
            last_ref = str(datetime.datetime.now()).split(' ')[0]
            cursor.execute(f"UPDATE all_users "
                           f"SET last_ref = '{last_ref}' "
                           f"WHERE user_id = {referer_id};")

            connection.commit()

    @staticmethod
    async def get_user(user_id):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            user_info = cursor.execute(f'SELECT * FROM all_users WHERE user_id = {user_id};').fetchall()
            return user_info

    @staticmethod
    async def get_all_user():
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            all_users = cursor.execute(f'SELECT * FROM all_users;').fetchall()
            return all_users

    @staticmethod
    async def star_rating(user_id, stars):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE all_users "
                           f"SET stars = stars + {stars} "
                           f"WHERE user_id = {user_id};")
            connection.commit()

    @staticmethod
    async def star_write_off(user_id, stars):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE all_users "
                           f"SET stars = stars - {stars} "
                           f"WHERE user_id = {user_id};")
            connection.commit()

    @staticmethod
    async def captcha_execute(user_id):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE all_users "
                           f"SET captcha = 'True' "
                           f"WHERE user_id = {user_id};")
            connection.commit()

    @staticmethod
    async def set_last_task(user_id):
        with sqlite3.connect('stars_base.db') as connection:
            last_task = str(datetime.datetime.now()).split(' ')[0]
            cursor = connection.cursor()
            cursor.execute(f"UPDATE all_users "
                           f"SET last_task = '{last_task}' "
                           f"WHERE user_id = {user_id};")
            connection.commit()

    @staticmethod
    async def set_last_bonus(user_id):
        with sqlite3.connect('stars_base.db') as connection:
            last_bonus = str(datetime.datetime.now()).split(' ')[0]
            cursor = connection.cursor()
            cursor.execute(f"UPDATE all_users "
                           f"SET last_bonus = '{last_bonus}' "
                           f"WHERE user_id = {user_id};")
            connection.commit()

    @staticmethod
    async def set_bonus(user_id, bonus):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE all_users "
                           f"SET bonus = {bonus} "
                           f"WHERE user_id = {user_id};")
            connection.commit()

    # ====================
    # Задания
    # ====================

    @staticmethod
    async def add_new_task(task_id, task_name, channel, channel_id, reward, complete_count, serial_number):
        """Вставляем новую задачу"""
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO tasks_list (task_id, task_name, channel, '
                           f'channel_id, reward, complete_count, serial_number) '
                           f'VALUES ("{task_id}", "{task_name}", "{channel}", '
                           f'{channel_id}, {reward}, {complete_count}, {serial_number});')
            connection.commit()

    @staticmethod
    async def get_all_tasks():
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            task_list = cursor.execute(f'SELECT * FROM tasks_list;').fetchall()
            return task_list

    @staticmethod
    async def delete_task(task_id):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM tasks_list WHERE task_id = '{task_id}';")
            connection.commit()

    @staticmethod
    async def new_task_name(task_id, new_task_name):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE tasks_list "
                           f"SET task_name =  '{new_task_name}' "
                           f"WHERE task_id = '{task_id}';")
            connection.commit()

    @staticmethod
    async def new_executor(task_id, who_complete_str):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE tasks_list "
                           f"SET who_complete =  '{who_complete_str}' "
                           f"WHERE task_id = '{task_id}';")
            connection.commit()

    @staticmethod
    async def edit_task_channel(task_id, new_channel):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE tasks_list "
                           f"SET channel =  '{new_channel}' "
                           f"WHERE task_id = '{task_id}';")
            connection.commit()

    @staticmethod
    async def edit_task_channel_id(task_id, new_channel_id):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE tasks_list "
                           f"SET channel_id =  {new_channel_id} "
                           f"WHERE task_id = '{task_id}';")
            connection.commit()

    @staticmethod
    async def edit_task_reward(task_id, reward):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE tasks_list "
                           f"SET reward =  '{reward}' "
                           f"WHERE task_id = '{task_id}';")
            connection.commit()

    @staticmethod
    async def edit_task_complete_count(task_id, complete_count):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE tasks_list "
                           f"SET complete_count =  {complete_count} "
                           f"WHERE task_id = '{task_id}';")
            connection.commit()

    # ====================
    # Сообщения
    # ====================

    @staticmethod
    async def settings_add(set_name, set_content):
        """Вставляем новую задачу"""
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO settings (set_name, set_content) '
                           f'VALUES ("{set_name}", "{set_content}")'
                           f'ON CONFLICT (set_name)'
                           f'DO UPDATE SET set_content = "{set_content}";')
            connection.commit()

    @staticmethod
    async def settings_get(set_name):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            task_list = cursor.execute(f'SELECT * FROM settings WHERE set_name = "{set_name}";').fetchall()
            return task_list[0]

    # ====================
    # Вывод звезд
    # ====================

    @staticmethod
    async def new_request_for_withdrawal_of_stars(user_id, username, requirement_stars):
        """Новая заявка на вывод звезд"""
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO stars_withdrawal (user_id, username, requirement_stars) '
                           f'VALUES ({user_id} ,"{username}", {requirement_stars})'
                           f'ON CONFLICT (username)'
                           f'DO UPDATE SET requirement_stars = {requirement_stars};')
            connection.commit()

    @staticmethod
    async def get_all_requests():
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            requests_list = cursor.execute(f'SELECT * FROM stars_withdrawal;').fetchall()
            return requests_list

    @staticmethod
    async def get_user_request(username):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            requests_list = cursor.execute(f'SELECT * FROM stars_withdrawal WHERE username = "{username}";').fetchall()
            return requests_list[0]

    @staticmethod
    async def remove_request(username):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM stars_withdrawal WHERE username = '{username}';")

    # ====================
    # Статистика
    # ====================

    @staticmethod
    async def get_statistic(today_int):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            stat = cursor.execute(f'SELECT * FROM statistic WHERE date_int = {today_int};').fetchall()
            return stat[0]

    @staticmethod
    async def stars_count(stars):
        with sqlite3.connect('stars_base.db') as connection:
            today = str(datetime.datetime.now()).split(' ')[0]
            date_int = await date_string_to_epoch(today)
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO statistic (date_int, stars_count) '
                           f'VALUES ({date_int} ,{stars})'
                           f'ON CONFLICT (date_int)'
                           f'DO UPDATE SET stars_count = stars_count + {stars};')
            connection.commit()

    @staticmethod
    async def task_count():
        with sqlite3.connect('stars_base.db') as connection:
            today = str(datetime.datetime.now()).split(' ')[0]
            date_int = await date_string_to_epoch(today)
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO statistic (date_int, task_count) '
                           f'VALUES ({date_int} , 1)'
                           f'ON CONFLICT (date_int)'
                           f'DO UPDATE SET task_count = task_count + 1;')
            connection.commit()
