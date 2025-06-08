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

welcome_text = (
    "👋 *Добро пожаловать в бота записи на массаж!*\n\n"
    "💆 *Мы предлагаем следующие виды массажа:*\n"
    "• Классический массаж (спины, шеи)\n"
    "• Релакс-массаж\n"
    "• Антицеллюлитный массаж\n"
    "• Спортивный массаж\n"
    "• Массаж головы и лица\n"
    "🔗 Подробнее о видах массажа: [Читать статью](https://telegra.ph/Kakie-byvayut-vidy-massazha-06-08)\n\n"
    "🕒 *Продолжительность сеанса:* от 30 до 60 минут\n"
    "💰 *Стоимость:* уточняйте при записи\n\n"
    "📍 *Адрес:* г. Минск, ул. Примерная, 12\n"
    "📞 *Телефон:* +375293541777\n"
    "📲 *Telegram:* @qwerty466\n\n"
    "Чтобы записаться на массаж — нажмите кнопку ниже ⬇️"
)



async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Админ — только кнопка, без текста
    if user_id == ADMIN_ID:
        keyboard = [
            [KeyboardButton("Все Записи")],
            [KeyboardButton("Удалить запись")],  # добавляем
            [KeyboardButton("📅 Календарь записей")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Посмотреть все записи:", reply_markup=reply_markup)
        return

    # Пользователь — меню с сообщением
    keyboard = [
    [KeyboardButton("Записаться на массаж")],
    [KeyboardButton("Мои Записи")],
    [KeyboardButton("Отменить запись")]
    ]
    

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
