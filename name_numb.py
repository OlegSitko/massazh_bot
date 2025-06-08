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
from records import save_records

NAME, PHONE, TIME = range(3)
# Имя
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["state"] = NAME
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("Теперь введите ваш номер телефона:")
    return PHONE

# Телефон с валидацией
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["state"] = PHONE
    phone = update.message.text.strip()
    if not re.fullmatch(r"\+?\d{10,15}", phone):
        await update.message.reply_text("Некорректный номер.")
        return PHONE

    context.user_data['phone'] = phone
    keyboard = [
        ["Сегодня в 16:00", "Сегодня в 18:00"],
        ["Завтра в 12:00", "Завтра в 15:00"],
        ["Отменить"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите время или введите своё:", reply_markup=reply_markup)
    return TIME

# Время + отправка + сохранение
async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["state"] = TIME
    chosen_time = update.message.text.strip()
    context.user_data['time'] = chosen_time
    name = context.user_data['name']
    phone = context.user_data['phone']
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    username_display = f"@{username}" if username else "🚫 нет username"

    # Проверка, занято ли время другим пользователем
    all_records = context.application.bot_data.get("records", {})
    for uid, rec_list in all_records.items():
        if uid != user_id:
            for record in rec_list:
                if record["time"] == chosen_time:
                    await update.message.reply_text(
                        f"❌ Время {chosen_time} уже занято. Пожалуйста, выберите другое."
                    )
                    return TIME  # остаёмся на этом шаге

    # Сохраняем заявку
    context.application.bot_data.setdefault("records", {})
    context.application.bot_data["records"].setdefault(user_id, []).append({
        "name": name,
        "phone": phone,
        "time": chosen_time
    })
     # 🧠 Сохраняем в JSON
    save_records(context.application.bot_data["records"])
    # Ответ пользователю
    keyboard = [
        [KeyboardButton("Мои Записи")],
        [KeyboardButton("На главную")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Спасибо, {name}!\n"
        f"Ваша заявка:\n📞 {phone}\n🕒 {chosen_time}",
        reply_markup=reply_markup
    )

    # Отправка админу
    admin_id = ADMIN_ID
    await context.bot.send_message(
        chat_id=admin_id,
        text=(
            f"📥 Новая заявка:\n"
            f"👤 Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"🕒 Время: {chosen_time}\n"
            f"🆔 Пользователь: {username_display}"
        )
    )

    return ConversationHandler.END