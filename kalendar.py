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
from datetime import datetime, date, timedelta  # Добавлен импорт datetime
from JSON import save_records
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
    keyboard = []

    for i, r in enumerate(found, 1):
        msg += (
            f"\n{i}. 👤 {r['name']}\n"
            f"📞 {r['phone']}\n"
            f"🕒 {r['time']}\n"
            f"🆔 {r['username']}\n"
        )
        keyboard.append(
            [InlineKeyboardButton(f"Удалить запись {i}", callback_data=f"delete_record_{i}")]
        )

    keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_admin_calendar")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(msg, reply_markup=reply_markup)

async def handle_delete_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("delete_record_"):
        return

    record_index = int(data.replace("delete_record_", "")) - 1
    all_records = context.application.bot_data.get("records", {})
    found = []

    for rec_list in all_records.values():
        for r in rec_list:
            found.append(r)

    if record_index < 0 or record_index >= len(found):
        await query.edit_message_text("⚠️ Ошибка: Запись не найдена.")
        return

    record_to_delete = found[record_index]
    
    for user_id, rec_list in all_records.items():
        if record_to_delete in rec_list:
            rec_list.remove(record_to_delete)
            if not rec_list:
                del all_records[user_id]
            break

    context.application.bot_data["records"] = all_records
    save_records(all_records)

    await query.edit_message_text(f"✅ Запись на {record_to_delete['time']} удалена.")
    await admin_calendar_view(update, context)

async def admin_calendar_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        user_id = update.callback_query.from_user.id
        if user_id != ADMIN_ID:
            await update.callback_query.message.reply_text("⛔️ Только администратор может просматривать все записи.")
            return
    elif update.message:
        user_id = update.message.from_user.id
        if user_id != ADMIN_ID:
            await update.message.reply_text("⛔️ Только администратор может просматривать все записи.")
            return
    else:
        return

    current_month = context.user_data.get("current_month", date.today().month)
    current_year = context.user_data.get("current_year", date.today().year)

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.itermonthdays(current_year, current_month)
    
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
            current_date = date(current_year, current_month, day).strftime("%d.%m.%Y")
            if current_date in booked_dates:
                text = f"{day}🟢"
                callback = f"admin_day_{current_date}"
            else:
                text = f"{day}"
                callback = f"day_{current_date}"

            week.append(InlineKeyboardButton(text, callback_data=callback))

        if len(week) == 7:
            keyboard.append(week)
            week = []

    if week:
        keyboard.append(week)

    # Кнопки навигации по месяцам
    keyboard.append([
        InlineKeyboardButton("<< Текущий месяц", callback_data="current_month"),
        InlineKeyboardButton("Следующий месяц >>", callback_data="next_month")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data["current_month"] = current_month
    context.user_data["current_year"] = current_year

    text = f"📅 Календарь на {calendar.month_name[current_month]} {current_year}:\n🟢 — есть запись (нажмите на дату)"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_month_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    current_month = context.user_data.get("current_month", date.today().month)
    current_year = context.user_data.get("current_year", date.today().year)

    if data == "current_month":
        current_month = date.today().month
        current_year = date.today().year
    elif data == "next_month":
        next_date = date(current_year, current_month, 1) + timedelta(days=31)
        if next_date > date.today() + timedelta(days=90):
            await query.answer("Запись доступна только на 3 месяца вперед", show_alert=True)
            return
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1

    context.user_data["current_month"] = current_month
    context.user_data["current_year"] = current_year

    if "Календарь записей" in query.message.text:  # Админский календарь
        await admin_calendar_view(update, context)
    else:  # Пользовательский календарь
        await inline_calendar_view(update, context)

async def inline_calendar_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_month = context.user_data.get("current_month", date.today().month)
    current_year = context.user_data.get("current_year", date.today().year)
    
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.itermonthdays(current_year, current_month)

    keyboard = []
    week = []

    for day in month_days:
        if day == 0:
            week.append(InlineKeyboardButton(" ", callback_data="ignore"))
        else:
            current_date = date(current_year, current_month, day)
            if current_date < date.today():  # Прошедшие даты
                week.append(InlineKeyboardButton("✖️", callback_data="ignore"))
            else:
                week.append(InlineKeyboardButton(
                    str(day), 
                    callback_data=f"day_{current_date.strftime('%d.%m.%Y')}"
                ))

        if len(week) == 7:
            keyboard.append(week)
            week = []

    if week:
        keyboard.append(week)

    # Кнопки навигации по месяцам
    keyboard.append([
        InlineKeyboardButton("<< Текущий месяц", callback_data="current_month"),
        InlineKeyboardButton("Следующий месяц >>", callback_data="next_month")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data["current_month"] = current_month
    context.user_data["current_year"] = current_year

    text = f"📅 Выберите дату ({calendar.month_name[current_month]} {current_year}):"
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if not data.startswith("day_"):
        return

    selected_date_str = data.replace("day_", "")
    selected_date = datetime.strptime(selected_date_str, "%d.%m.%Y").date()
    
    if selected_date < date.today():
        await query.answer("Нельзя выбрать прошедшую дату", show_alert=True)
        return

    context.user_data["selected_date"] = selected_date_str

    times = ["10:00", "12:00", "14:00", "16:00", "18:00"]
    keyboard = [
        [InlineKeyboardButton(t, callback_data=f"time_{t}")] for t in times
    ]
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_dates")])

    await query.edit_message_text(
        f"Вы выбрали дату: *{selected_date_str}*\nВыберите время:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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

    all_records = context.application.bot_data.get("records", {})
    for uid, rec_list in all_records.items():
        for record in rec_list:
            if record["time"] == full_slot:
                times = ["10:00", "12:00", "14:00", "16:00", "18:00"]
                keyboard = [
                    [InlineKeyboardButton(t, callback_data=f"time_{t}")] for t in times
                ]
                keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_dates")])
                
                await query.edit_message_text(
                    f"❌ Время {full_slot} уже занято.\n\nВыберите другое время:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return

    context.application.bot_data.setdefault("records", {})
    context.application.bot_data["records"].setdefault(user_id, []).append({
        "name": name,
        "phone": phone,
        "time": full_slot,
        "username": username
    })
    save_records(context.application.bot_data["records"])

    keyboard = [
        [KeyboardButton("Мои Записи")],
        [KeyboardButton("На главную")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=user_id,
        text=(f"Спасибо, {name}!\n"
              f"Ваша заявка:\n📞 {phone}\n🕒 {full_slot}\n\n"
              f"Если есть вопросы — свяжитесь с администратором:\n"
              f"Telegram: @qwerty4666\nТелефон: +375293541777"),
        reply_markup=reply_markup
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(f"📥 Новая заявка:\n"
              f"👤 Имя: {name}\n"
              f"📞 Телефон: {phone}\n"
              f"🕒 Время: {full_slot}\n"
              f"🆔 Пользователь: {username}")
    )

async def handle_back_to_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await inline_calendar_view(update, context)