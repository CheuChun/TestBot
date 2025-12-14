import asyncio
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

def split_text(text: str, limit: int = 4096):
    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 <= limit:
            current += line + "\n"
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


def payment_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Оплатить", pay=True)
    return builder.as_markup()