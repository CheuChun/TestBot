import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery
from aiogram.utils.formatting import Text
from dotenv import load_dotenv
from logging_config import logger
from history import add_message, get_history
from ai_handler import call_openrouter
from payment import load_paid_users, save_paid_users, payment_keyboard
from style import split_text, animate_dots

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
paid_users = load_paid_users()


@dp.message(Command("start"))
async def start_command(message: types.Message):
    content = Text(
        "Рад вас приветствовать, ",
        message.from_user.full_name,
        ". Чем могу помочь?"
    )
    await message.answer(**content.as_kwargs())

@dp.message(Command("pay"))
async def donate_handler(message: types.Message):
    prices = [LabeledPrice(label="XTR", amount=1)]
    await message.answer_invoice(
        title="Оплата",
        description="Доступ к ИИ-собеседнику",
        prices=prices,
        provider_token="",
        payload="bot_access",
        currency="XTR",
        reply_markup=payment_keyboard()
    )

@dp.pre_checkout_query()
async def pre_checkout_handler(query: PreCheckoutQuery):
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def success_payment_handler(message: types.Message):
    user_id = message.from_user.id
    paid_users.add(user_id)
    save_paid_users(paid_users)
    await message.answer("✅ Оплата прошла успешно. Доступ открыт!")


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    if user_id not in paid_users:
        await message.answer(
            "🔒 Для продолжения необходимо оплатить доступ. Используйте команду /pay"
        )
        return

    user_text = message.text
    add_message(user_id, "user", user_text)
    context = get_history(user_id)

    loading = await message.answer("⏳ Ваш ИИ-собеседник думает")
    animation_task = asyncio.create_task(animate_dots(loading))
    raw_response = await call_openrouter(context)
    response = raw_response.strip() if raw_response else ""
    animation_task.cancel()

    if not response:
        await loading.edit_text("Ваш покорный ИИ-собеседник не смог сформировать ответ(")
        return

    add_message(user_id, "assistant", response)

    parts = split_text(response)
    await loading.edit_text(parts[0])
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
