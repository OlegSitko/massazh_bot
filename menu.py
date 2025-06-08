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




async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Админ — только кнопка, без текста
    if user_id == ADMIN_ID:
        keyboard = [
            [KeyboardButton("Все Записи")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Посмотреть все записи:", reply_markup=reply_markup)
        return

    # Пользователь — меню с сообщением
    keyboard = [
        [KeyboardButton("Записаться на массаж")],
        [KeyboardButton("Мои Записи")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)
