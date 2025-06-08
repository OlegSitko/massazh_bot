import re
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)
from config import ADMIN_ID
from config import BOT_TOKEN
from menu import menu

NAME, PHONE, TIME = range(3)

# Начало записи
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["state"] = NAME
    keyboard = [[KeyboardButton("Отменить")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Введите ваше имя:", reply_markup=reply_markup)
    return NAME

# Отменить — полная отмена и возврат в меню
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await cancel(update, context)

# Полная отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("Записаться на массаж")],
        [KeyboardButton("Мои Записи")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Запись отменена. Вы можете начать заново:", reply_markup=reply_markup)
    return ConversationHandler.END

# На главную
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await menu(update, context)
