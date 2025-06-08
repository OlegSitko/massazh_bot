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
import json
import os



# Мои записи

async def my_records(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"[LOG] Получено сообщение: {update.message.text!r}")  # <-- лог в консоль
    user_id = update.message.from_user.id
    records = context.application.bot_data.get("records", {}).get(user_id)

    if not records:
        await update.message.reply_text("У вас пока нет записей.")
        return

    message = "📋 Ваши записи:"
    for i, r in enumerate(records, 1):
        message += f"\n{i}. {r['name']} | {r['phone']} | {r['time']}"
    await update.message.reply_text(message)

async def all_records(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = ADMIN_ID
    user_id = update.message.from_user.id

    if user_id != admin_id:
        await update.message.reply_text("⛔ Эта команда доступна только администратору.")
        return

    all_data = context.application.bot_data.get("records", {})
    if not all_data:
        await update.message.reply_text("Записей пока нет.")
        return

    msg = "📋 Все записи клиентов:\n"
    for uid, records in all_data.items():
        for r in records:
            username = f"@{update.message.from_user.username}" if update.message.from_user.username else "неизвестно"
            msg += f"\n👤 {r['name']} | 📞 {r['phone']} | 🕒 {r['time']} | 🆔 {uid}"

    await update.message.reply_text(msg)

RECORDS_FILE = "records.json"

# Загрузка данных из файла
def load_records():
    if os.path.exists(RECORDS_FILE):
        try:
            with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}  # файл пустой
                return json.loads(content)
        except json.JSONDecodeError:
            print("[ERROR] Невозможно загрузить JSON. Файл повреждён.")
            return {}
    return {}


# Сохранение данных в файл
def save_records(data):
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
