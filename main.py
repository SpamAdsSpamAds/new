from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

TOKEN = "1970454158:AAGPh2dEwz1Z18p6EoPDQnyZlGRwTN1l5l8"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


def check(in_str: str) -> bool:
    return bool(in_str)


def calc(string: str) -> int:
    return eval(string)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(msg: types.Message):
    await msg.reply(f"Приятно познакомиться,{msg.from_user.first_name}")


@dp.message_handler(content_types=["text"])
async def get_text_messages(msg: types.Message):
    answer = "Не работает"
    if check(msg.text.lower()):
        answer = calc(msg.text.lower())

    await msg.answer(answer)


if __name__ == "__main__":
    executor.start_polling(dp)
