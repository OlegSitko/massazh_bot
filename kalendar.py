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
import calendar
from records import my_records, all_records, cancel_record, save_records, load_records
from datetime import date, timedelta
from config import ADMIN_ID
from config import BOT_TOKEN
import json
import os
from telegram import KeyboardButton

async def handle_admin_day_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if not data.startswith("admin_day_"):
        return

    selected_date = data.replace("admin_day_", "")
    all_records = context.application.bot_data.get("records", {})
    found = []

    for rec_list in all_records.values():
        for r in rec_list:
            if r["time"].startswith(selected_date):
                found.append(r)

    if not found:
        await query.edit_message_text(f"На {selected_date} записей не найдено.")
        return

    msg = f"📅 Записи на {selected_date}:\n"
    for i, r in enumerate(found, 1):
        msg += (
            f"\n{i}. 👤 {r['name']}\n"
            f"📞 {r['phone']}\n"
            f"🕒 {r['time']}\n"
            f"🆔 {r['username']}\n"
        )

    await query.edit_message_text(msg)


async def admin_calendar_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today()
    year, month = today.year, today.month
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.itermonthdays(year, month)

    all_records = context.application.bot_data.get("records", {})
    booked_dates = set()

    for rec_list in all_records.values():
        for r in rec_list:
            match = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", r["time"])
            if match:
                booked_dates.add(match.group(0))

    keyboard = []
    week = []

    for day in month_days:
        if day == 0:
            week.append(InlineKeyboardButton(" ", callback_data="ignore"))
        else:
            current_date = date(year, month, day).strftime("%d.%m.%Y")
            if current_date in booked_dates:
                text = f"{day}🟢"
                callback = f"admin_day_{current_date}"
            else:
                text = f"{day}"
                callback = "ignore"

            week.append(InlineKeyboardButton(text, callback_data=callback))

        if len(week) == 7:
            keyboard.append(week)
            week = []

    if week:
        keyboard.append(week)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"📅 Календарь на {calendar.month_name[month]} {year}:\n🟢 — есть запись (нажмите на дату)",
        reply_markup=reply_markup
    )


async def inline_calendar_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today()
    year, month = today.year, today.month
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.itermonthdays(year, month)

    keyboard = []
    week = []

    for day in month_days:
        if day == 0:
            week.append(InlineKeyboardButton(" ", callback_data="ignore"))
        else:
            week.append(InlineKeyboardButton(str(day), callback_data=f"day_{day}"))

        if len(week) == 7:
            keyboard.append(week)
            week = []

    if week:
        keyboard.append(week)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📅 Выберите дату ({calendar.month_name[month]} {year}):",
        reply_markup=reply_markup
    )


async def handle_day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if not data.startswith("day_"):
        return

    selected_day = int(data.split("_")[1])
    today = date.today()
    selected_date = date(today.year, today.month, selected_day)
    formatted = selected_date.strftime("%d.%m.%Y")

    # Сохраняем выбранную дату в user_data
    context.user_data["selected_date"] = formatted

    # Кнопки с временем
    times = ["10:00", "12:00", "14:00", "16:00", "18:00"]
    keyboard = [[InlineKeyboardButton(t, callback_data=f"time_{t}")] for t in times]
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_dates")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"Вы выбрали дату: *{formatted}*\nВыберите время:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def handle_back_to_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔙 Возврат к выбору даты...")
    await inline_calendar_view(update, context)


async def handle_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if not data.startswith("time_"):
        return

    selected_time = data.split("_")[1]
    selected_date = context.user_data.get("selected_date")

    if not selected_date:
        await query.edit_message_text("⚠️ Не выбрана дата.")
        return

    full_slot = f"{selected_date} в {selected_time}"

    user = query.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "неизвестно"
    name = context.user_data.get("name", user.first_name)
    phone = context.user_data.get("phone", "не указан")

    # Проверка занятости
    all_records = context.application.bot_data.get("records", {})
    for uid, rec_list in all_records.items():
        for record in rec_list:
            if record["time"] == full_slot:
                # Повторно показать выбор времени
                times = ["10:00", "12:00", "14:00", "16:00", "18:00"]
                keyboard = [[InlineKeyboardButton(t, callback_data=f"time_{t}")] for t in times]
                keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_dates")])
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    f"❌ Время {full_slot} уже занято.\n\nВыберите другое время:",
                    reply_markup=reply_markup
                )
                return


    # Сохраняем
    context.application.bot_data.setdefault("records", {})
    context.application.bot_data["records"].setdefault(user_id, []).append({
        "name": name,
        "phone": phone,
        "time": full_slot,
        "username": username
    })
    save_records(context.application.bot_data["records"])

    # Сообщение пользователю
    keyboard = [
        [KeyboardButton("Мои Записи")],
        [KeyboardButton("На главную")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            f"Спасибо, {name}!\n"
            f"Ваша заявка:\n📞 {phone}\n🕒 {full_slot}\n\n"
            f"Если есть вопросы — свяжитесь с администратором:\n"
            f"Telegram: @qwerty4666\nТелефон: +375293541777"
        ),
        reply_markup=reply_markup
    )

    # Сообщение админу
    from config import ADMIN_ID
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"📥 Новая заявка:\n"
            f"👤 Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"🕒 Время: {full_slot}\n"
            f"🆔 Пользователь: {username}"
        )
    )
