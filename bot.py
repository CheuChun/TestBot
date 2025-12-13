import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.formatting import Text
from dotenv import load_dotenv
from logging_config import logger
from history import add_message, get_history
from ai_handler import call_openrouter

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def split_text(text: str, limit: int = 4096):
    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 <= limit:
            current += (line + "\n") if current else (line + "\n")
        else:
            words = line.split()
            for word in words:
                if len(current) + len(word) + 1 > limit:
                    chunks.append(current.rstrip("\n"))
                    current = word + " "
                else:
                    current += word + " "
            current = current.rstrip() + "\n"
    if current:
        chunks.append(current.rstrip("\n"))
    return chunks

@dp.message(Command(commands=["start"]))
async def start_command(message: types.Message):
    content = Text(
        "Рад вас приветствовать, ",
        message.from_user.full_name,
        ". Чем могу помочь?"
    )
    await message.answer(**content.as_kwargs())

async def animate_dots(msg: types.Message):
    dots = ""
    while True:
        await asyncio.sleep(0.4)
        dots += "."
        if len(dots) > 3:
            dots = ""
        try:
            await msg.edit_text(f"⏳ Ваш ИИ-собеседник думает{dots}")
        except:
            break


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    add_message(user_id, "user", user_text)
    context = get_history(user_id)
    loading_msg = await message.answer("⏳ Ваш ИИ-собеседник думает")

    animation_task = asyncio.create_task(animate_dots(loading_msg))
    raw_response = await call_openrouter(context)
    response = raw_response.strip() if raw_response else ""
    animation_task.cancel()

    if not response:
        await loading_msg.edit_text("Ваш покорный ИИ-собеседник не смог сформировать ответ(")
        return

    add_message(user_id, "assistant", response)

    parts = split_text(response)
    await loading_msg.edit_text(parts[0])
    for part in parts[1:]:
        await message.answer(part)


async def main():
    try:
        logger.info("Бот запущен")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
