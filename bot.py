import logging
import csv
import os
import json
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)

# 🔑 Настройки
TOKEN = os.getenv("BOT_TOKEN") or "ТВОЙ_ТОКЕН"
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-1003014842866"))
PRIVACY_URL = "https://docs.google.com/document/d/19eJqUD_zbSmc7_ug07XXYr25cV4BATTqBQwgsgdGX0U/edit?usp=sharing"

# 📌 Ссылки и медиа
WEB_APP_URL = "https://khvgvni.github.io/Cabinet/"
ROUTE_IMG = "https://raw.githubusercontent.com/Khvgvni/Cabinet/68248242d6ba3a80bc1d2c5d86f4c003e4b18cfb/Road%20map.jpg"
INVITE_IMG = "https://raw.githubusercontent.com/Khvgvni/Cabinet/d3ef68f9ae102683d9c5c5dd797d163aa02c3566/Invitation.png"
DESTINATION = "Забайкальский край, Чита, Ленинградская улица, 15А"
END_LAT, END_LON = 52.033938, 113.500514  # координаты

# 📌 Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 📌 Состояния
(
    REG_NAME, REG_PHONE,
    TABLE_NAME, TABLE_PHONE, TABLE_COMMENT,
    TEAM_NAME, TEAM_PHONE, TEAM_ROLE,
    WAITING_LOCATION
) = range(9)


# ---------- УТИЛИТЫ ----------
def nav_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])


# ---------- СТАРТ ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🎭 Афиша", callback_data="show_afisha")],
        [InlineKeyboardButton("🔶 Пройти регистрацию", callback_data="register")]
    ]
    text = (
        "👋 Привет! Добро пожаловать в чат-бот *Cabinet!* 🎉\n\n"
        "Здесь вы можете получить информацию о грядущих событиях, "
        "забронировать стол, получить билет и воспользоваться другими функциями.\n\n"
        "✨ У нас также есть мини-приложение с красивым интерфейсом.\n\n"
        f"Проходя регистрацию вы соглашаетесь с [политикой конфиденциальности]({PRIVACY_URL})"
    )
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb),
                                    parse_mode="Markdown", disable_web_page_preview=True)


# ---------- МЕНЮ ----------
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎪 Открыть мини-приложение", url=WEB_APP_URL)],
        [InlineKeyboardButton("🍽 Забронировать стол", callback_data="book_table")],
        [InlineKeyboardButton("🚕 Заказать такси", callback_data="order_taxi")],
        [InlineKeyboardButton("🎟 Получить пригласительный", callback_data="invite")],
        [InlineKeyboardButton("👥 Хочу в команду", callback_data="join_team")],
        [InlineKeyboardButton("🎭 Афиша", callback_data="show_afisha")]
    ])
    text = "📌 Главное меню:\nВыберите действие:"
    await update.message.reply_text(text, reply_markup=kb)


# ---------- БРОНЬ ----------
async def book_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Введите ваше ФИО:")
    return TABLE_NAME

async def table_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["table_name"] = update.message.text
    await update.message.reply_text("📞 Введите ваш телефон:")
    return TABLE_PHONE

async def table_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["table_phone"] = update.message.text
    await update.message.reply_text("💬 Добавьте комментарий (или напишите - нет):")
    return TABLE_COMMENT

async def table_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["table_comment"] = update.message.text

    msg = (
        f"🍽 Новая бронь!\n\n"
        f"👤 {context.user_data['table_name']}\n"
        f"📞 {context.user_data['table_phone']}\n"
        f"💬 {context.user_data['table_comment']}"
    )
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
    await update.message.reply_text("✅ Уважаемый гость, стол забронирован! Ждём Вас!", reply_markup=nav_keyboard())
    return ConversationHandler.END


# ---------- WEBAPP ДАННЫЕ ----------
async def handle_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
        logger.info(f"📩 Получены данные из WebApp: {data}")

        if data["type"] == "booking":
            msg = (
                f"🍽 Новая бронь (WebApp)!\n\n"
                f"👤 ФИО: {data.get('name')}\n"
                f"📞 Телефон: {data.get('phone')}"
            )
            await update.message.reply_text("✅ Ваш стол забронирован! Ждём Вас!")
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)

        elif data["type"] == "team":
            msg = (
                f"👥 Новая заявка в команду (WebApp)!\n\n"
                f"👤 ФИО: {data.get('name')}\n"
                f"📞 Телефон: {data.get('phone')}\n"
                f"💼 Должность: {data.get('role')}"
            )
            await update.message.reply_text("✅ В течение недели администратор свяжется с вами!")
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)

        elif data["type"] == "invite":
            await update.message.reply_text("🎟 Вот ваш пригласительный!")
            await update.message.reply_photo(INVITE_IMG)

    except Exception as e:
        logger.error(f"Ошибка обработки web_app_data: {e}")
        await update.message.reply_text("⚠️ Ошибка обработки данных из мини-приложения.")


# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()

    # Бронь
    conv_table = ConversationHandler(
        entry_points=[CallbackQueryHandler(book_table, pattern="book_table")],
        states={
            TABLE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, table_name)],
            TABLE_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, table_phone)],
            TABLE_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, table_comment)],
        },
        fallbacks=[CommandHandler("cancel", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_table)
    app.add_handler(MessageHandler(filters.WEB_APP_DATA, handle_webapp))

    print("🤖 Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
