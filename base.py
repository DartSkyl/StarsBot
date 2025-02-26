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
                           'referral TEXT'
                           ');')

            # Таблица с заданиями
            cursor.execute('CREATE TABLE IF NOT EXISTS tasks_list ('
                           'task_id INTEGER PRIMARY KEY, '
                           'channels_list TEXT,'
                           'reward INT,  '  # Всегда делить на 100
                           'who_complete TEXT DEFAULT empty'
                           ');')

            connection.commit()

    # ====================
    # Пользователи
    # ====================

    @staticmethod
    async def add_new_user(user_id):
        """Вставляем сразу все столбцы"""
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO all_users (user_id, referral) '
                           f'VALUES ({user_id}, "empty")')
            connection.commit()

    @staticmethod
    async def get_user(user_id):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            user_info = cursor.execute(f'SELECT * FROM all_users WHERE user_id = {user_id};').fetchall()
            return user_info

    @staticmethod
    async def save_referer(user_id, new_ref_list):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE all_users "
                           f"SET referral = '{new_ref_list}' "
                           f"WHERE user_id = {user_id};")

    @staticmethod
    async def star_rating(user_id, stars):
        with sqlite3.connect('stars_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE all_users "
                           f"SET stars = stars + {stars} "
                           f"WHERE user_id = {user_id};")

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
                           f"SET who_complete =  {who_complete_str} "
                           f"WHERE task_id = {task_id};")
