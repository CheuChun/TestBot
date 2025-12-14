import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery
from aiogram.utils.formatting import Text
from dotenv import load_dotenv
from logging_config import logger
from ai_handler import call_openrouter
from style import split_text, animate_dots, payment_keyboard
from database import init_db, get_user, add_user, update_user
from models import MODELS

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    content = Text(
        "Рад вас приветствовать, ",
        message.from_user.full_name,
        ". Чем могу помочь?"
    )
    await message.answer(**content.as_kwargs())
    await message.answer(
        "Вы можете переключить вашего ИИ-собеседника на GPT с помощью команды /gpt "
        "или на LLaMA командой /llama. \n\nКоманда для просмотра текущей модели /model "
    )


@dp.message(Command("pay"))
async def cmd_pay(message: types.Message):
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


@dp.message(Command("llama"))
async def cmd_switch_llama(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await add_user(message.from_user.id)
        user = await get_user(message.from_user.id)
    user.current_model = MODELS["llama"]["id"]
    await update_user(user)
    await message.answer(f"Модель переключена на {MODELS['llama']['title']} ✅")


@dp.message(Command("gpt"))
async def cmd_switch_gpt(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await add_user(message.from_user.id)
        user = await get_user(message.from_user.id)
    user.current_model = MODELS["gpt"]["id"]
    await update_user(user)
    await message.answer(f"Модель переключена на {MODELS['gpt']['title']} ✅")


@dp.message(Command("model"))
async def cmd_model(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Модель ещё не выбрана. Используется LLaMA по умолчанию.")
        return
    for model in MODELS.values():
        if model["id"] == user.current_model:
            await message.answer(f"Текущая модель: {model['title']}")
            return


@dp.pre_checkout_query()
async def pay_pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def pay_success(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await add_user(message.from_user.id, paid=True)
    else:
        user.paid = True
        await update_user(user)
    await message.answer("✅ Оплата прошла успешно. Доступ открыт!")


@dp.message()
async def message_handler(message: types.Message):
    user = await get_user(message.from_user.id)

    if not user or not user.paid:
        await message.answer(
            "🔒 Для продолжения необходимо оплатить доступ. Используйте команду /pay"
        )
        return

    user_text = message.text
    history = user.history.get(user.current_model, [])
    history.append({"role": "user", "content": user_text})
    loading = await message.answer("⏳ Ваш ИИ-собеседник думает")
    animation_task = asyncio.create_task(animate_dots(loading))
    raw_response = await call_openrouter(history, model=user.current_model)
    response = raw_response.strip() if raw_response else ""
    animation_task.cancel()

    if not response:
        await loading.edit_text("Ваш покорный ИИ-собеседник не смог сформировать ответ(")
        return

    history.append({"role": "assistant", "content": response})
    user.history[user.current_model] = history
    await update_user(user)

    parts = split_text(response)
    await loading.edit_text(parts[0])
    for part in parts[1:]:
        await message.answer(part)


async def main():
    await init_db()

    logger.info("Бот запущен")
    await dp.start_polling(bot)
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
