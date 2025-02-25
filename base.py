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
                           'stars INT DEFAULT 1,'
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
