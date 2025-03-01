import sqlite3


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
                           'captcha VARCHAR(155) DEFAULT "False");')

            # Таблица с заданиями
            cursor.execute('CREATE TABLE IF NOT EXISTS tasks_list ('
                           'task_id INTEGER PRIMARY KEY, '
                           'channels_list TEXT,'
                           'reward INT,  '  # Всегда делить на 100
                           'who_complete TEXT'
                           ');')

            # Таблица с настройками
            cursor.execute('CREATE TABLE IF NOT EXISTS settings ('
                           'set_name VARCHAR(155) PRIMARY KEY, '
                           'set_content TEXT'
                           ');')

            connection.commit()

    # ====================
    # Пользователи
    # ====================

    @staticmethod
    async def add_new_user(user_id, referer_id):
        """Вставляем сразу все столбцы"""
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()

            cursor.execute(f'INSERT INTO all_users (user_id, referer) '
                           f'VALUES ({user_id}, {referer_id})')

            # И сразу посчитаем рефереру его сучку
            cursor.execute(f"UPDATE all_users "
                           f"SET referral_count = referral_count + 1 "
                           f"WHERE user_id = {referer_id};")

            connection.commit()

    @staticmethod
    async def get_user(user_id):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            user_info = cursor.execute(f'SELECT * FROM all_users WHERE user_id = {user_id};').fetchall()
            return user_info

    @staticmethod
    async def star_rating(user_id, stars):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE all_users "
                           f"SET stars = stars + {stars} "
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

    # ====================
    # Задания
    # ====================

    @staticmethod
    async def add_new_task(task_id, channels_list, reward):
        """Вставляем новую задачу"""
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO tasks_list (task_id, channels_list, reward) '
                           f'VALUES ({task_id}, "{channels_list}", {reward})')
            connection.commit()

    @staticmethod
    async def new_executor(task_id, who_complete_str):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE tasks_list "
                           f"SET who_complete =  '{who_complete_str}' "
                           f"WHERE task_id = {task_id};")
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
            cursor.execute(f"DELETE FROM tasks_list WHERE task_id = {task_id};")
            connection.commit()

    @staticmethod
    async def edit_task_channels(task_id, new_channels):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE tasks_list "
                           f"SET channels_list =  '{new_channels}' "
                           f"WHERE task_id = {task_id};")
            connection.commit()

    @staticmethod
    async def edit_task_reward(task_id, reward):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE tasks_list "
                           f"SET reward =  '{reward}' "
                           f"WHERE task_id = {task_id};")
            connection.commit()

    # ====================
    # Задания
    # ====================

    @staticmethod
    async def settings_add(set_name, set_content):
        """Вставляем новую задачу"""
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO settings (set_name, set_content) '
                           f'VALUES ("{set_name}", "{set_content}");')
            connection.commit()

    @staticmethod
    async def settings_change(set_name, set_content):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE settings "
                           f"SET set_content =  '{set_content}' "
                           f"WHERE set_name = {set_name};")
            connection.commit()

    @staticmethod
    async def settings_get(set_name):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            task_list = cursor.execute(f'SELECT * FROM settings WHERE set_name = "{set_name}";').fetchall()
            return task_list[0]
