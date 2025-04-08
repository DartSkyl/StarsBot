import sqlite3
import datetime
import asyncpg as apg


async def date_string_to_epoch(date_string):
    dt = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    epoch_seconds = int(dt.timestamp())
    return epoch_seconds


class BotBase:
    """Класс для реализации базы данных и методов для взаимодействия с ней"""

    def __init__(self, _db_user, _db_pass, _db_name, _db_host):
        self.db_name = _db_name
        self.db_user = _db_user
        self.db_pass = _db_pass
        self.db_host = _db_host
        self.pool = None

    async def connect(self):
        """Для использования БД будем использовать пул соединений.
        Иначе рискуем поймать asyncpg.exceptions._base.InterfaceError: cannot perform operation:
        another operation is in progress. А нам это не надо"""
        self.pool = await apg.create_pool(
            database=self.db_name,
            user=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            max_inactive_connection_lifetime=10,
            min_size=1,
            max_size=100
        )

    async def check_db_structure(self):
        """Создаем при первом подключении, а в последующем проверяем, таблицы необходимые для работы бота"""
        async with self.pool.acquire() as connection:
            await connection.execute("CREATE TABLE IF NOT EXISTS all_users ("
                                     "user_id INTEGER PRIMARY KEY,"
                                     "stars INT DEFAULT 100,"  # Всегда делить на 100
                                     "referer INTEGER DEFAULT 0,"  # Будем записывать каждому того, кто его привел
                                     "referral_count INTEGER DEFAULT 0,"
                                     "captcha VARCHAR(155),"
                                     "last_task VARCHAR(155) DEFAULT 'empty',"  # Когда последний раз выполнял задание
                                     "last_ref VARCHAR(155) DEFAULT 'empty', " # Когда привел последнего реферала
                                     "last_bonus VARCHAR(155) DEFAULT 'empty',"  # Когда активировал бонус
                                     "bonus INTEGER DEFAULT 1,"
                                     "username VARCHAR(155));")  # Кол-во бонусов подряд, "n"

            # Таблица с заданиями
            await connection.execute("CREATE TABLE IF NOT EXISTS tasks_list ("
                                     "task_id VARCHAR(155) PRIMARY KEY, "
                                     "task_name TEXT, "
                                     "channel TEXT, "
                                     "channel_id INTEGER, "
                                     "reward INT,  "  # Всегда делить на 100
                                     "who_complete TEXT, "
                                     "complete_count INTEGER, "
                                     "serial_number INTEGER UNIQUE"
                                     ");")

            # Таблица с настройками
            await connection.execute("CREATE TABLE IF NOT EXISTS settings ("
                                     "set_name VARCHAR(155) PRIMARY KEY, "
                                     "set_content TEXT"
                                     ");")

            # Таблица с заявками на вывод звезд
            await connection.execute("CREATE TABLE IF NOT EXISTS stars_withdrawal ("
                                     "user_id INTEGER,"
                                     "username VARCHAR(155) PRIMARY KEY, "
                                     "requirement_stars INTEGER"
                                     ");")

            # Таблица со статистикой
            await connection.execute("CREATE TABLE IF NOT EXISTS statistic ("
                                     "date_int INTEGER PRIMARY KEY,"
                                     "task_count INTEGER DEFAULT 0, "
                                     "stars_count INTEGER DEFAULT 0"
                                     ");")

    # ====================
    # Пользователи
    # ====================

    async def add_new_user(self, user_id, referer_id, username):
        """Вставляем сразу все столбцы"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.all_users (user_id, referer, username, captcha) "
                                     f"VALUES ({user_id}, {referer_id}, '{username}', 'False')")

            # И сразу посчитаем рефереру его сучку
            await connection.execute(f"UPDATE public.all_users "
                                     f"SET referral_count = referral_count + 1 "
                                     f"WHERE user_id = {referer_id};")

            # И обновим last_ref реферера
            last_ref = str(datetime.datetime.now()).split(' ')[0]
            await connection.execute(f"UPDATE public.all_users "
                                     f"SET last_ref = '{last_ref}' "
                                     f"WHERE user_id = {referer_id};")

    async def get_user(self, user_id):
        async with self.pool.acquire() as connection:
            user_info = await connection.fetch(f"SELECT * FROM public.all_users WHERE user_id = {user_id};")
            return user_info

    async def get_all_user(self):
        async with self.pool.acquire() as connection:
            all_users = await connection.fetch(f"SELECT * FROM public.all_users;")
            return all_users

    async def star_rating(self, user_id, stars):
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.all_users "
                                     f"SET stars = all_users.stars + {stars} "
                                     f"WHERE user_id = {user_id};")

    async def star_write_off(self, user_id, stars):
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.all_users "
                                     f"SET stars = all_users.stars - {stars} "
                                     f"WHERE user_id = {user_id};")

    async def captcha_execute(self, user_id):
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.all_users "
                                     f"SET captcha = 'True' "
                                     f"WHERE user_id = {user_id};")

    async def set_last_task(self, user_id):
        last_task = str(datetime.datetime.now()).split(' ')[0]
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.all_users "
                                     f"SET last_task = '{last_task}' "
                                     f"WHERE user_id = {user_id};")

    async def set_last_bonus(self, user_id):
        last_bonus = str(datetime.datetime.now()).split(' ')[0]
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.all_users "
                                     f"SET last_bonus = '{last_bonus}' "
                                     f"WHERE user_id = {user_id};")

    async def set_bonus(self, user_id, bonus):
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.all_users "
                                     f"SET bonus = {bonus} "
                                     f"WHERE user_id = {user_id};")

    # ====================
    # Задания
    # ====================

    async def add_new_task(self, task_id, task_name, channel, channel_id, reward, complete_count, serial_number):
        """Вставляем новую задачу"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.tasks_list (task_id, task_name, channel, "
                                     f"channel_id, reward, complete_count, serial_number) "
                                     f"VALUES ('{task_id}', '{task_name}', '{channel}', "
                                     f"{channel_id}, {reward}, {complete_count}, {serial_number});")

    async def get_all_tasks(self):
        async with self.pool.acquire() as connection:
            task_list = await connection.fetch(f"SELECT * FROM public.tasks_list ORDER BY serial_number;")
        return task_list

    async def delete_task(self, task_id):
        async with self.pool.acquire() as connection:
            await connection.execute(f"DELETE FROM public.tasks_list WHERE task_id = '{task_id}';")

    async def new_task_name(self, task_id, new_task_name):
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.tasks_list "
                                     f"SET task_name =  '{new_task_name}' "
                                     f"WHERE task_id = '{task_id}';")

    async def new_executor(self, task_id, who_complete_str):
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.tasks_list "
                                     f"SET who_complete =  '{who_complete_str}' "
                                     f"WHERE task_id = '{task_id}';")

    async def edit_task_channel(self, task_id, new_channel):
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.tasks_list "
                                     f"SET channel =  '{new_channel}' "
                                     f"WHERE task_id = '{task_id}';")

    async def edit_task_channel_id(self, task_id, new_channel_id):
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.tasks_list "
                                     f"SET channel_id =  {new_channel_id} "
                                     f"WHERE task_id = '{task_id}';")

    async def edit_task_reward(self, task_id, reward):
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.tasks_list "
                                     f"SET reward =  '{reward}' "
                                     f"WHERE task_id = '{task_id}';")

    async def edit_task_complete_count(self, task_id, complete_count):
        async with self.pool.acquire() as connection:
            await connection.execute(f"UPDATE public.tasks_list "
                                     f"SET complete_count =  {complete_count} "
                                     f"WHERE task_id = '{task_id}';")

    # ====================
    # Сообщения
    # ====================

    # async def settings_add(self, set_name, set_content):
    #     """Вставляем новую задачу"""
    #     async with self.pool.acquire() as connection:
    #         await connection.execute(f'INSERT INTO public.settings ("set_name", "set_content") '
    #                                  f'VALUES ("{set_name}", "{set_content}") '
    #                                  f'ON CONFLICT ("set_name")'
    #                                  f'DO UPDATE SET set_content = "{set_content}";')
    #         connection.commit()

    async def settings_add(self, set_name, set_content):
        """Вставляем новую задачу"""
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO public.settings (set_name, set_content)
                VALUES ($1, $2)
                ON CONFLICT (set_name)
                DO UPDATE SET set_content = $2;
                """,
                set_name,
                set_content
            )

    async def settings_get(self, set_name):
        async with self.pool.acquire() as connection:
            task_list = await connection.fetch(
                """
                SELECT * FROM public.settings WHERE set_name = $1;
                """,
                set_name
            )
        return task_list[0]

    # ====================
    # Вывод звезд
    # ====================

    async def new_request_for_withdrawal_of_stars(self, user_id, username, requirement_stars):
        """Новая заявка на вывод звезд"""
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.stars_withdrawal (user_id, username, requirement_stars) "
                                     f"VALUES ({user_id} ,'{username}', {requirement_stars})"
                                     f"ON CONFLICT (username)"
                                     f"DO UPDATE SET requirement_stars = {requirement_stars};")

    async def get_all_requests(self):
        async with self.pool.acquire() as connection:
            requests_list = await connection.fetch(f"SELECT * FROM public.stars_withdrawal;")
        return requests_list

    async def get_user_request(self, username):
        async with self.pool.acquire() as connection:
            requests_list = await connection.fetch(f"SELECT * FROM public.stars_withdrawal WHERE username = '{username}';")
            return requests_list[0]

    async def remove_request(self, username):
        async with self.pool.acquire() as connection:
            await connection.execute(f"DELETE FROM public.stars_withdrawal WHERE username = '{username}';")

    # ====================
    # Статистика
    # ====================

    async def get_statistic(self, today_int):
        async with self.pool.acquire() as connection:
            stat = await connection.fetch(f"SELECT * FROM public.statistic WHERE date_int = {today_int};")
            return stat[0]

    async def stars_count(self, stars):
        today = str(datetime.datetime.now()).split(' ')[0]
        date_int = await date_string_to_epoch(today)
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.statistic (date_int, stars_count) "
                                     f"VALUES ({date_int} ,{stars})"
                                     f"ON CONFLICT (date_int)"
                                     f"DO UPDATE SET stars_count = statistic.stars_count + {stars};")

    async def task_count(self):
        today = str(datetime.datetime.now()).split(' ')[0]
        date_int = await date_string_to_epoch(today)
        async with self.pool.acquire() as connection:
            await connection.execute(f"INSERT INTO public.statistic (date_int, task_count) "
                                     f"VALUES ({date_int} , 1)"
                                     f"ON CONFLICT (date_int)"
                                     f"DO UPDATE SET task_count = statistic.task_count + 1;")

    # ====================
    # Для проверки выполнения заданий
    # ====================

    async def check_task_complete(self, user_id):
        async with self.pool.acquire() as connection:
            users = await connection.fetch(f"SELECT * FROM public.task_check;")
            users = [u['user_id'] for u in users]
            if user_id in users:
                return True
            return False
