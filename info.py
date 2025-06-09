import re
from telegram import (
    Update,
    ReplyKeyboardMarkup,
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
from kalendar import inline_calendar_view
from config import ADMIN_ID
from JSON import save_records

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
    await inline_calendar_view(update, context)  # Вместо показа времени — вызываем календарь
    return ConversationHandler.END

# Время + отправка + сохранение
async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["state"] = TIME
    chosen_time = update.message.text.strip()
    context.user_data['time'] = chosen_time
    name = context.user_data['name']
    phone = context.user_data['phone']
    username = f"@{update.message.from_user.username}" if update.message.from_user.username else "неизвестно"
    
    selected_date = context.user_data.get("selected_date")  # Получаем выбранную дату
    if not selected_date:
        await update.message.reply_text("⚠️ Не выбрана дата.")
        return TIME

    # Ответ пользователю
    keyboard = [
        [KeyboardButton("Мои Записи")],
        [KeyboardButton("На главную")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    admin_us = "@qwerty4666"
    admin_tel = "+375293541777"
    await update.message.reply_text(
        f"Спасибо, {name}!\n"
        f"Ваша заявка:\n📞 {phone} "
        f"\n🕒 {chosen_time}\n\n"
        f"Если у вас есть вопросы — свяжитесь с администратором по телеграмм: {admin_us} \n"
        f"Или по телефону: {admin_tel}",
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
            f"🆔 Пользователь: {username}"
        )
    )

    return ConversationHandler.END