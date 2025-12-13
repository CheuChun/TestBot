import os
import json
from aiogram.utils.keyboard import InlineKeyboardBuilder

PAYMENTS_FILE = "paid_users.json"

def load_paid_users():
    if not os.path.exists(PAYMENTS_FILE):
        return set()
    with open(PAYMENTS_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))

def save_paid_users(users):
    with open(PAYMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users), f)

def payment_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Оплатить", pay=True)
    return builder.as_markup()