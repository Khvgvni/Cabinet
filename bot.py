import logging
import json
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
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

# 📌 Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------- СТАРТ ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🎪 Открыть мини-приложение", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton("🍽 Забронировать стол", callback_data="book_table")],
        [InlineKeyboardButton("🚕 Заказать такси", callback_data="order_taxi")],
        [InlineKeyboardButton("🎟 Получить пригласительный", callback_data="invite")],
        [InlineKeyboardButton("👥 Хочу в команду", callback_data="join_team")],
        [InlineKeyboardButton("🎭 Афиша", callback_data="show_afisha")]
    ]
    text = (
        "👋 Привет! Добро пожаловать в чат-бот *Cabinet!* 🎉\n\n"
        "Здесь вы можете:\n"
        "🍽 Забронировать стол\n"
        "🎟 Получить пригласительный\n"
        "🚕 Вызвать такси\n"
        "👥 Подать заявку в команду\n\n"
        "✨ У нас есть [мини-приложение] для красивого интерфейса.\n\n"
        f"⚖️ Проходя регистрацию вы соглашаетесь с [политикой конфиденциальности]({PRIVACY_URL})\n\n"
        "_P.S. Я создан, чтобы наполнить твой вечер самыми яркими эмоциями 😉_"
    )
    if update.message:
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown", disable_web_page_preview=True
        )
    else:
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown", disable_web_page_preview=True
        )


# ---------- ОБРАБОТКА ДАННЫХ ИЗ WEBAPP ----------
async def webapp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
        logger.info(f"Получены данные из WebApp: {data}")

        if data.get("type") == "booking":
            msg = (
                f"🍽 Новая заявка на бронь!\n\n"
                f"👤 {data['name']}\n"
                f"📞 {data['phone']}"
            )
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
            await update.message.reply_text("✅ Ваша заявка принята! Мы с вами свяжемся.")

        elif data.get("type") == "ticket":
            msg = (
                f"🎟 Новый запрос пригласительного!\n\n"
                f"👤 {data['name']}\n"
                f"📞 {data['phone']}\n"
                f"Количество: {data['count']}"
            )
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
            await update.message.reply_text("✅ Ваш пригласительный отправлен!")

        elif data.get("type") == "team":
            msg = (
                f"👥 Новая заявка в команду!\n\n"
                f"💼 Должность: {data['role']}\n"
                f"👤 {data['name']}\n"
                f"📞 {data['phone']}"
            )
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
            await update.message.reply_text("✅ Заявка отправлена! Администратор свяжется с вами.")

        elif data.get("type") == "taxi":
            msg = (
                f"🚕 Новый заказ такси!\n\n"
                f"📍 Откуда: {data['from']}\n"
                f"⏰ Время: {data['time']}"
            )
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
            await update.message.reply_text("✅ Такси заказано! 🚖")

    except Exception as e:
        logger.error(f"Ошибка WebApp: {e}")
        await update.message.reply_text("⚠️ Ошибка при обработке данных.")


# ---------- ПРОЧИЕ ВКЛАДКИ ----------
async def show_afisha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("🎭 Афиша: (сюда будут загружаться ближайшие события)")


async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_photo(INVITE_IMG, caption="🎟 Ваш пригласительный!")


async def order_taxi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺 Схема проезда", callback_data="show_route")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])
    await q.message.edit_text("🚕 Выберите действие:", reply_markup=kb)


async def show_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_photo(ROUTE_IMG, caption=f"📍 Наш адрес: {DESTINATION}")
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]])
    await q.message.reply_text("Что дальше?", reply_markup=kb)


# ---------- ОБРАБОТКА КНОПОК ----------
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if data == "invite":
        return await invite(update, context)
    elif data == "order_taxi":
        return await order_taxi(update, context)
    elif data == "show_route":
        return await show_route(update, context)
    elif data == "show_afisha":
        return await show_afisha(update, context)
    elif data == "main_menu":
        return await start(update, context)


# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_handler))

    print("🤖 Бот запущен с WebApp API!")
    app.run_polling()


if __name__ == "__main__":
    main()
