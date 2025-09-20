import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)

# 🔑 Настройки
TOKEN = "ТВОЙ_ТОКЕН"  # вставь сюда токен своего бота
GROUP_CHAT_ID = -1003014842866  # ID твоей админ-группы

# 📌 Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния диалога
ASK_NAME, ASK_PHONE = range(2)


# ---------- СТАРТ ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🍽 Забронировать стол", callback_data="book_table")],
        [InlineKeyboardButton("🚕 Заказать такси", callback_data="order_taxi")],
        [InlineKeyboardButton("🎟 Получить пригласительный", callback_data="invite")],
        [InlineKeyboardButton("👥 Хочу в команду", callback_data="join_team")],
    ]
    text = (
        "👋 Привет! Добро пожаловать в чат-бот *Cabinet!* 🎉\n\n"
        "Выберите действие:"
    )
    await update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )


# ---------- БРОНИРОВАНИЕ ----------
async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("👤 Введите ваше ФИО:")
    return ASK_NAME


async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📞 Введите ваш телефон:")
    return ASK_PHONE


async def finish_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    name = context.user_data.get("name")

    msg = (
        f"🍽 Новая заявка на бронь!\n\n"
        f"👤 {name}\n"
        f"📞 {phone}"
    )
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
    await update.message.reply_text("✅ Ваша заявка принята! Мы с вами свяжемся.")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Бронирование отменено.")
    return ConversationHandler.END


# ---------- ПРОЧИЕ ВКЛАДКИ ----------
async def order_taxi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("🚕 Такси пока заказываем вручную 🙂")


async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("🎟 Ваш пригласительный!")


async def join_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("👥 Заявка в команду отправлена!")


# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()

    # Меню
    app.add_handler(CommandHandler("start", start))

    # Бронирование через ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_booking, pattern="^book_table$")],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish_booking)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)

    # Остальные кнопки
    app.add_handler(CallbackQueryHandler(order_taxi, pattern="^order_taxi$"))
    app.add_handler(CallbackQueryHandler(invite, pattern="^invite$"))
    app.add_handler(CallbackQueryHandler(join_team, pattern="^join_team$"))

    print("🤖 Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
