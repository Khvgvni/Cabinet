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
TOKEN = "8259299108:AAENuDFq8sb2OysuUacFQETMdhJg1LM-jmw"
GROUP_CHAT_ID = -1003014842866
PRIVACY_URL = "https://docs.google.com/document/d/19eJqUD_zbSmc7_ug07XXYr25cV4BATTqBQwgsgdGX0U/edit?usp=sharing"

# 📌 Ссылки и медиа
WEB_APP_URL = "https://khvgvni.github.io/Cabinet/"
ROUTE_IMG = "https://raw.githubusercontent.com/Khvgvni/Cabinet/68248242d6ba3a80bc1d2c5d86f4c003e4b18cfb/Road%20map.jpg"
INVITE_IMG = "https://raw.githubusercontent.com/Khvgvni/Cabinet/d3ef68f9ae102683d9c5c5dd797d163aa02c3566/Invitation.png"
DESTINATION = "Забайкальский край, Чита, Ленинградская улица, 15А"
END_LAT, END_LON = 52.033938, 113.500514

# 📌 Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 📌 Состояния
(
    REG_NAME, REG_PHONE,
    TABLE_NAME, TABLE_PHONE, TABLE_DATE, TABLE_TIME, TABLE_COMMENT,
    TEAM_NAME, TEAM_PHONE, TEAM_ROLE,
    WAITING_LOCATION
) = range(11)


# ---------- УТИЛИТЫ ----------
def nav_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]])


def get_user_data(user_id: int):
    try:
        with open("users.csv", "r", encoding="utf-8") as f:
            r = csv.reader(f, delimiter=";")
            next(r, None)
            for row in r:
                if len(row) >= 3 and row[2] == str(user_id):
                    return row
    except FileNotFoundError:
        return None
    return None


def is_registered(user_id: int) -> bool:
    return get_user_data(user_id) is not None


# ---------- СТАРТ ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if is_registered(user_id):
        return await show_main_menu(update, context)

    kb = [
        [InlineKeyboardButton("🎭 Афиша", callback_data="show_afisha")],
        [InlineKeyboardButton("🔶 Пройти регистрацию", callback_data="register")]
    ]
    text = (
        "👋 Привет! Добро пожаловать в чат-бот *Cabinet!* 🎉\n\n"
        "Здесь вы можете получить информацию о грядущих событиях или, пройдя простую регистрацию, "
        "забронировать стол, получить билет на ивент и воспользоваться другими полезными функциями.\n\n"
        "✨ У нас также есть мини-приложение с красивым интерфейсом.\n\n"
        f"Проходя регистрацию вы соглашаетесь с [политикой конфиденциальности]({PRIVACY_URL})\n\n"
        "_P.S. Я создан, чтобы наполнить твой вечер самыми яркими эмоциями 😉_"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb),
                                        parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb),
                                                      parse_mode="Markdown", disable_web_page_preview=True)


# ---------- МЕНЮ ----------
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎪 Открыть мини-приложение", web_app={"url": WEB_APP_URL})],
        [InlineKeyboardButton("🍽 Забронировать стол", callback_data="book_table")],
        [InlineKeyboardButton("🚕 Заказать такси", callback_data="order_taxi")],
        [InlineKeyboardButton("🎟 Получить пригласительный", callback_data="invite")],
        [InlineKeyboardButton("👥 Хочу в команду", callback_data="join_team")],
        [InlineKeyboardButton("🎭 Афиша", callback_data="show_afisha")]
    ])
    text = "📌 Главное меню:\nВыберите действие:"
    if update.message:
        await update.message.reply_text(text, reply_markup=kb)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=kb)


# ---------- ОБРАБОТКА ДАННЫХ ИЗ WEBAPP ----------
async def webapp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
        logger.info(f"Получены данные из WebApp: {data}")

        if data.get("type") == "booking":
            msg = (
                f"🍽 Новая бронь!\n\n"
                f"👤 {data['name']}\n"
                f"📞 {data['phone']}\n"
                f"📅 {data['date']} ⏰ {data['time']}\n"
                f"💬 {data['comment']}"
            )
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
            await update.message.reply_text("✅ Ваш столик забронирован! Ждём Вас 🎉")

        elif data.get("type") == "ticket":
            msg = (
                f"🎟 Новый запрос пригласительного!\n\n"
                f"👤 {data['name']}\n"
                f"📞 {data['phone']}"
            )
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
            await update.message.reply_text("✅ Ваш пригласительный отправлен! 🎭")

        elif data.get("type") == "team":
            msg = (
                f"👥 Новая заявка в команду!\n\n"
                f"💼 Должность: {data['role']}\n"
                f"👤 {data['name']}\n"
                f"📞 {data['phone']}"
            )
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
            await update.message.reply_text("✅ Заявка отправлена! Администратор свяжется с вами.")

    except Exception as e:
        logger.error(f"Ошибка WebApp: {e}")
        await update.message.reply_text("⚠️ Ошибка при обработке данных.")


# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_main_menu, pattern="main_menu"))
    app.add_handler(CallbackQueryHandler(show_main_menu))  # fallback
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_handler))

    print("🤖 Бот запущен с WebApp API!")
    app.run_polling()


if __name__ == "__main__":
    main()
