from aiogram.types import Message
from aiogram.filters import Command

from utils.admin_router import admin_router


# @admin_router.message(Command('start'))
# async def start_func(msg: Message):
#     msg_text = ('Здравствуйте, уроки ещё на монтаже.\n'
#                 'Сейчас добавьтесь в тг-канал (ссылка) https://t.me/pytcksebe\n'
#                 'Как уроки будут готовы, мы вам сообщим.')
#     await msg.answer(msg_text)
