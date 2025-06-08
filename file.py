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
from config import BOT_TOKEN
from menu import menu
from name_numb import get_name, get_phone, get_time
from start import start, go_back, cancel, back_to_menu
from records import my_records, all_records
from records import load_records

# Состояния
NAME, PHONE, TIME = range(3)


# Запуск
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
   # Загружаем записи
    app.bot_data["records"] = load_records()
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^Записаться на массаж$"), start)],
        states={
            NAME: [
                MessageHandler(filters.TEXT & filters.Regex("^Отменить$"), go_back),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_name),
            ],
            PHONE: [
                MessageHandler(filters.TEXT & filters.Regex("^Отменить$"), go_back),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
            TIME: [
                MessageHandler(filters.TEXT & filters.Regex("^Отменить$"), go_back),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_time),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.TEXT & filters.Regex("^Отменить$"), go_back),
        ],
    )

    app.add_handler(CommandHandler("start", menu))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Мои Записи$"), my_records))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^На главную$"), back_to_menu))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Все Записи$"), all_records))

    app.run_polling()

if __name__ == '__main__':
    main()
    menu()