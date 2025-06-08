# main.py — объединённая и исправленная версия

import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, CallbackQueryHandler, filters
)
from config import BOT_TOKEN
from menu import menu
from info import get_name, get_phone  # get_time удалён
from start import start, step_back as go_back, cancel, back_to_menu
from kalendar import (
    handle_back_to_dates,
    handle_day_selection,
    handle_time_selection,
    handle_admin_day_click
)
from records import (
    my_records, all_records,
    cancel_record, confirm_cancel,
    admin_delete_record, confirm_admin_delete,
    load_records
)

NAME, PHONE, TIME = range(3)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.bot_data["records"] = load_records()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Записаться на массаж$"), start)],
        states={
            NAME: [
                MessageHandler(filters.TEXT & filters.Regex("^◀️ Назад$"), go_back),
                MessageHandler(filters.TEXT & filters.Regex("^На главную$"), back_to_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_name),
            ],
            PHONE: [
                MessageHandler(filters.TEXT & filters.Regex("^◀️ Назад$"), go_back),
                MessageHandler(filters.TEXT & filters.Regex("^На главную$"), back_to_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
            TIME: [
                 MessageHandler(filters.TEXT & filters.Regex("^◀️ Назад$"), go_back),
                MessageHandler(filters.TEXT & filters.Regex("^На главную$"), back_to_menu),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ]
        },
        fallbacks=[
            MessageHandler(filters.TEXT & filters.Regex("^На главную$"), back_to_menu)
        ]
    )

    cancel_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Отменить запись$"), cancel_record)],
        states={
            100: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_cancel)]
        },
        fallbacks=[MessageHandler(filters.TEXT & filters.Regex("^На главную$"), back_to_menu)]
    )

    delete_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Удалить запись$"), admin_delete_record)],
        states={
            200: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_admin_delete)]
        },
        fallbacks=[MessageHandler(filters.TEXT & filters.Regex("^На главную$"), back_to_menu)]
    )

    app.add_handler(CommandHandler("start", menu))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(conv_handler)
    app.add_handler(cancel_conv)
    app.add_handler(delete_conv)
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Мои Записи$"), my_records))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Все Записи$"), all_records))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^На главную$"), back_to_menu))
    app.add_handler(CallbackQueryHandler(handle_day_selection, pattern="^day_"))
    app.add_handler(CallbackQueryHandler(handle_time_selection, pattern="^time_"))
    app.add_handler(CallbackQueryHandler(handle_admin_day_click, pattern="^admin_day_"))
    app.add_handler(CallbackQueryHandler(handle_back_to_dates, pattern="^back_to_dates$"))

    app.run_polling()


if __name__ == '__main__':
    main()
