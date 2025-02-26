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

            connection.commit()

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
