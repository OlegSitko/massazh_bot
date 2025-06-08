import re
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    CallbackQueryHandler
)
from config import ADMIN_ID
from config import BOT_TOKEN
import json
import os

# Мои записи

async def my_records(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Загрузка из файла при необходимости
    if "records" not in context.application.bot_data:
        context.application.bot_data["records"] = load_records()

    records = context.application.bot_data["records"].get(str(user_id)) or context.application.bot_data["records"].get(user_id)

    if not records:
        await update.message.reply_text("У вас пока нет записей.")
        return

    message = "📋 Ваши записи:"
    for i, r in enumerate(records, 1):
        message += (
            f"\n{i}. {r['name']}"
            f"\n   📞 {r['phone']}"
            f"\n   🕒 {r['time']}\n"
        )
    await update.message.reply_text(message)

#################################################################################
# Все Записи
async def all_records(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = ADMIN_ID
    user_id = update.message.from_user.id

    if user_id != admin_id:
        await update.message.reply_text("⛔ Эта команда доступна только администратору.")
        return

    # Данные с JSON
    all_data = context.application.bot_data.get("records", {})
    if not all_data:
        await update.message.reply_text("Записей пока нет.")
        return

    msg = "📋 Все записи клиентов:\n"
    counter = 1  # <-- номер записи

    for uid, records in all_data.items():
        for r in records:
            username = f"@{r['username']}" if r.get("username") else "неизвестно"
            msg += (
                f"№{counter}:\n"
                f"👤 {r['name']}\n"
                f"📞 {r['phone']}\n"
                f"🕒 {r['time']}\n"
                f"🆔 Пользователь: {username}\n\n"
            )
            counter += 1

    await update.message.reply_text(msg)

# Запуск удаления
async def admin_delete_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Эта команда только для администратора.")
        return

    all_data = context.application.bot_data.get("records", {})
    if not all_data:
        await update.message.reply_text("Записей нет.")
        return

    # Сохраняем все записи в список
    all_entries = []
    msg = "🗑 Выберите номер записи для удаления:\n"
    counter = 1
    for uid, records in all_data.items():
        for rec in records:
            username = f"@{rec['username']}" if rec.get("username") else "неизвестно"
            all_entries.append((uid, rec))
            msg += (
                f"\n№{counter}:\n"
                f"👤 {rec['name']}\n"
                f"📞 {rec['phone']}\n"
                f"🕒 {rec['time']}\n"
                f"🆔 {username}\n"
            )
            counter += 1

    if not all_entries:
        await update.message.reply_text("Нет записей для удаления.")
        return

    context.user_data["all_entries"] = all_entries
    await update.message.reply_text(msg + "\nВведите номер записи для удаления:")
    return 200  # новое состояние

async def confirm_admin_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Введите номер записи, например: 3")
        return 200

    index = int(text) - 1
    all_entries = context.user_data.get("all_entries")
    if not all_entries or index >= len(all_entries):
        await update.message.reply_text("Такой записи нет.")
        return 200

    uid, rec = all_entries[index]
    context.application.bot_data["records"][uid].remove(rec)

    # Если список стал пустым — удаляем ключ
    if not context.application.bot_data["records"][uid]:
        del context.application.bot_data["records"][uid]

    from records import save_records
    save_records(context.application.bot_data["records"])

    await update.message.reply_text(f"✅ Запись удалена: {rec['name']} | {rec['phone']} | {rec['time']}")
    return ConversationHandler.END


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


# Отмена записи пользователем
async def cancel_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    records = context.application.bot_data.get("records", {}).get(user_id)
 
 # Загрузка из файла при необходимости
    if "records" not in context.application.bot_data:
        context.application.bot_data["records"] = load_records()

    records = context.application.bot_data["records"].get(str(user_id)) or context.application.bot_data["records"].get(user_id)

    if not records:
        await update.message.reply_text("У вас нет записей для удаления.")
        return

    # Сохраняем записи в user_data и предлагаем выбрать
    context.user_data["cancel_options"] = records
    msg = "Выберите номер записи для удаления:\n"
    for i, r in enumerate(records, 1):
        msg += (
        f"№{i}:\n"
        f"👤 {r['name']}\n"
        f"📞 {r['phone']}\n"
        f"🕒 {r['time']}\n\n"
        )

          
    msg += "\nВведите номер записи для удаления (например, 2):"
    await update.message.reply_text(msg)
    return 100  # новое состояние

async def confirm_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Пожалуйста, введите корректный номер.")
        return 100

    index = int(text) - 1
    records = context.user_data.get("cancel_options")

    if index < 0 or index >= len(records):
        await update.message.reply_text("Такой записи нет.")
        return 100

    removed = records.pop(index)
    user_id = update.message.from_user.id
    context.application.bot_data["records"][user_id] = records
    from records import save_records
    save_records(context.application.bot_data["records"])

    await update.message.reply_text(f"✅ Запись на {removed['time']} удалена.")
    return ConversationHandler.END
