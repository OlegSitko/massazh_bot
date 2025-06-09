import json
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, CallbackQueryHandler, filters
)

RECORDS_FILE = "records.json"

# Функция для загрузки данных из файла
def load_all_records(app):
    all_records = load_records()  # Загружаем записи из файла
    app.bot_data["records"] = all_records  # Сохраняем в bot_data
    print("Загруженные записи в bot_data:", app.bot_data["records"])

# Функция для загрузки данных из файла
def load_records():
    if os.path.exists(RECORDS_FILE):
        try:
            with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    print("[WARNING] Файл пуст.")
                    return {}
                data = json.loads(content)
                print("[INFO] Данные успешно загружены:", data)
                return data
        except json.JSONDecodeError as e:
            print(f"[ERROR] Невозможно декодировать JSON: {e}")
            return {}
    else:
        print("[ERROR] Файл не найден.")
        return {}

# Функция для сохранения данных в файл
def save_records(data):
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Функция для добавления новой записи
def save_user_record(user_id, record, context):
    # Загружаем текущие записи
    all_records = context.application.bot_data.get("records", {})

    # Если записи для пользователя нет, создаем новый список
    if user_id not in all_records:
        all_records[user_id] = []

    # Проверка, существует ли запись с таким временем
    existing_record = next((r for r in all_records[user_id] if r["time"] == record["time"]), None)
    if existing_record:
        print(f"Запись на {record['time']} для {user_id} уже существует.")
        return  # Если запись уже существует, не добавляем новую

    # Добавляем запись в список
    all_records[user_id].append(record)

    # Обновляем bot_data и сохраняем в файл
    context.application.bot_data["records"] = all_records
    save_records(all_records)  # Сохраняем изменения в файл

    print(f"Запись добавлена для пользователя {user_id}: {record}")
