import re
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler
)
from config import ADMIN_ID
from menu import menu

NAME, PHONE, TIME = range(3)

# Начало записи
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["state"] = NAME
    keyboard = [[KeyboardButton("◀️ Назад")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Введите ваше имя:", reply_markup=reply_markup)
    return NAME

# Назад — шаг назад
async def step_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    current = context.user_data.get("state")

    if current == PHONE:
        context.user_data["state"] = NAME
        await update.message.reply_text("Введите ваше имя:")
        return NAME

    elif current == TIME:
        context.user_data["state"] = PHONE
        await update.message.reply_text("Введите номер телефона:")
        return PHONE

    elif current == NAME:
        # если на первом шаге — выйти в меню
        await update.message.reply_text("Вы вернулись в меню.")
        await menu(update, context)
        return ConversationHandler.END

    else:
        await update.message.reply_text("Нечего отменять.")
        return ConversationHandler.END

# Отмена и возврат в меню
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    keyboard = [
        [KeyboardButton("Записаться на массаж")],
        [KeyboardButton("Мои Записи")],
        [KeyboardButton("Отменить запись")],
        [KeyboardButton("📆 🗓 Выбрать дату")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Запись отменена. Вы вернулись в меню:", reply_markup=reply_markup)
    return ConversationHandler.END

# На главную
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await menu(update, context)
