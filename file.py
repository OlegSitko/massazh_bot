import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, CallbackQueryHandler, filters
)
from config import BOT_TOKEN
from menu import menu
from info import get_name, get_phone, get_time
from start import start, step_back as go_back, cancel, back_to_menu
from kalendar import (
    handle_back_to_dates,
    handle_day_selection,
    handle_time_selection,
    handle_admin_day_click,
    inline_calendar_view,
    admin_calendar_view,
    handle_month_navigation
)
from records import (
    my_records, all_records,
    cancel_record, confirm_cancel,
    admin_delete_record, confirm_admin_delete,
    load_records, save_records
)
from JSON import load_all_records
NAME, PHONE, TIME = range(3)



def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    load_all_records(app)

    # Обработчики сообщений
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
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_time),
            ]
        },
        fallbacks=[
            MessageHandler(filters.TEXT & filters.Regex("^На главную$"), back_to_menu)
        ]
    )

    # Команды администратора
    app.add_handler(CommandHandler("start", menu))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Мои Записи$"), my_records))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Все Записи$"), all_records))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^На главную$"), back_to_menu))
    app.add_handler(CommandHandler("all_records", all_records))  # Команда для просмотра всех записей
    app.add_handler(CallbackQueryHandler(handle_day_selection, pattern="^day_"))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📅 Календарь записей$"), admin_calendar_view))
    app.add_handler(CallbackQueryHandler(handle_admin_day_click, pattern="^admin_day_"))
    app.add_handler(MessageHandler(filters.TEXT, inline_calendar_view))  # Добавить обработчик календаря
    app.add_handler(CallbackQueryHandler(handle_time_selection, pattern="^time_"))
    app.add_handler(CallbackQueryHandler(handle_month_navigation, pattern="^(prev_month|next_month)$"))
    app.add_handler(CallbackQueryHandler(admin_calendar_view, pattern="^admin_day_"))

    app.run_polling()

if __name__ == '__main__':
    main()
