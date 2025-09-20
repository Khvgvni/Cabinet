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
TOKEN = os.getenv("8259299108:AAENuDFq8sb2OysuUacFQETMdhJg1LM-jmw") or "8259299108:AAENuDFq8sb2OysuUacFQETMdhJg1LM-jmw"
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-1003014842866"))
PRIVACY_URL = "https://docs.google.com/document/d/19eJqUD_zbSmc7_ug07XXYr25cV4BATTqBQwgsgdGX0U/edit?usp=sharing"

# 📌 Ссылки и медиа
WEB_APP_URL = "https://khvgvni.github.io/Cabinet/"
ROUTE_IMG = "https://raw.githubusercontent.com/Khvgvni/Cabinet/68248242d6ba3a80bc1d2c5d86f4c003e4b18cfb/Road%20map.jpg"
INVITE_IMG = "https://raw.githubusercontent.com/Khvgvni/Cabinet/d3ef68f9ae102683d9c5c5dd797d163aa02c3566/Invitation.png"
END_LAT, END_LON = 52.033938, 113.500514  # точные координаты клуба

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
        [InlineKeyboardButton("🎪 Открыть мини-приложение", url=WEB_APP_URL)],
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


# ---------- РЕГИСТРАЦИЯ ----------
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("✍️ Введите ваше ФИО:")
    return REG_NAME

async def reg_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reg_name"] = update.message.text
    await update.message.reply_text("📞 Введите ваш телефон:")
    return REG_PHONE

async def reg_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reg_phone"] = update.message.text
    user_id = update.effective_user.id

    with open("users.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([context.user_data["reg_name"], context.user_data["reg_phone"], user_id])

    await update.message.reply_text("✅ Регистрация завершена!", reply_markup=nav_keyboard())
    return ConversationHandler.END


# ---------- БРОНЬ ----------
async def book_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("Введите ваше ФИО:")
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
    user_id = update.effective_user.id

    with open("tables.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            context.user_data["table_name"], context.user_data["table_phone"],
            context.user_data["table_comment"], user_id
        ])

    msg = (
        f"🍽 Новая бронь!\n\n"
        f"👤 {context.user_data['table_name']}\n"
        f"📞 {context.user_data['table_phone']}\n"
        f"💬 {context.user_data['table_comment']}"
    )
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)

    await update.message.reply_text("✅ Уважаемый гость, стол забронирован! Ждём Вас!", reply_markup=nav_keyboard())
    return ConversationHandler.END


# ---------- ТАКСИ ----------
async def order_taxi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺 Схема проезда", callback_data="show_route")],
        [InlineKeyboardButton("🚕 Вызвать такси", callback_data="send_location")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])
    await q.message.edit_text("🚕 Выберите действие:", reply_markup=kb)

async def show_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_photo(ROUTE_IMG, caption=f"📍 Координаты клуба: {END_LAT}, {END_LON}")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])
    await q.message.reply_text("Что дальше?", reply_markup=kb)

async def send_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📍 Отправить мою геолокацию", request_location=True)]],
        one_time_keyboard=True, resize_keyboard=True
    )
    await q.message.reply_text("📍 Отправьте свою геолокацию:", reply_markup=kb)
    return WAITING_LOCATION

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.location:
        lat, lon = update.message.location.latitude, update.message.location.longitude
        url = (
    f"https://3.redirect.appmetrica.yandex.com/route?"
    f"start-lat={lat}&start-lon={lon}"
    f"&end-lat={END_LAT}&end-lon={END_LON}"
    f"&end-text=Забайкальский+край,+Чита,+Ленинградская+15А"
)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🚕 Построить маршрут в Яндекс Go", url=url)]])
        await update.message.reply_text("✅ Маршрут готов!", reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text("Нажмите кнопку ниже, чтобы вызвать такси:", reply_markup=kb)
        await update.message.reply_text("🏠 Вернуться в меню", reply_markup=nav_keyboard())
        return ConversationHandler.END


# ---------- ХОЧУ В КОМАНДУ ----------
async def join_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("✍️ Введите ваше ФИО:")
    return TEAM_NAME

async def team_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["team_name"] = update.message.text
    await update.message.reply_text("📞 Введите ваш телефон:")
    return TEAM_PHONE

async def team_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["team_phone"] = update.message.text
    await update.message.reply_text("💼 Укажите интересующую должность:")
    return TEAM_ROLE

async def team_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["team_role"] = update.message.text
    user_id = update.effective_user.id

    with open("team.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            context.user_data["team_name"], context.user_data["team_phone"],
            context.user_data["team_role"], user_id
        ])

    msg = (
        f"👥 Новая заявка в команду!\n\n"
        f"👤 {context.user_data['team_name']}\n"
        f"📞 {context.user_data['team_phone']}\n"
        f"💼 {context.user_data['team_role']}"
    )
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)

    await update.message.reply_text(
        "✅ В течение недели администратор свяжется с вами!\nХорошего вам дня! 🌸",
        reply_markup=nav_keyboard()
    )
    return ConversationHandler.END


# ---------- ПРИГЛАСИТЕЛЬНЫЙ ----------
async def send_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_photo(INVITE_IMG, caption="🎟 Ваш пригласительный!")
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]])
    await q.message.reply_text("Вы можете вернуться в главное меню:", reply_markup=kb)


# ---------- АФИША ----------
async def show_afisha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("🎭 Афиша: (сюда будут загружаться ближайшие события)", reply_markup=nav_keyboard())


# ---------- WEBAPP ДАННЫЕ ----------
async def handle_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
        logger.info(f"📩 Получены данные из WebApp: {data}")

        if data["type"] == "booking":
            msg = (
                f"🍽 Новая бронь (WebApp)!\n\n"
                f"👤 ФИО: {data.get('name')}\n"
                f"📞 Телефон: {data.get('phone')}\n"
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


# ---------- ОБРАБОТКА КНОПОК ----------
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if data == "register":
        return await register(update, context)
    elif data == "book_table":
        return await book_table(update, context)
    elif data == "order_taxi":
        return await order_taxi(update, context)
    elif data == "show_route":
        return await show_route(update, context)
    elif data == "send_location":
        return await send_location(update, context)
    elif data == "join_team":
        return await join_team(update, context)
    elif data == "invite":
        return await send_invite(update, context)
    elif data == "show_afisha":
        return await show_afisha(update, context)
    elif data == "main_menu":
        return await show_main_menu(update, context)


# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()

    # Регистрация
    conv_reg = ConversationHandler(
        entry_points=[CallbackQueryHandler(register, pattern="register")],
        states={
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_name)],
            REG_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_phone)],
        },
        fallbacks=[CommandHandler("cancel", start)],
    )

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

    # Такси
    conv_taxi = ConversationHandler(
        entry_points=[CallbackQueryHandler(send_location, pattern="send_location")],
        states={
            WAITING_LOCATION: [MessageHandler(filters.LOCATION, handle_location)],
        },
        fallbacks=[CommandHandler("cancel", start)],
    )

    # Команда
    conv_team = ConversationHandler(
        entry_points=[CallbackQueryHandler(join_team, pattern="join_team")],
        states={
            TEAM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, team_name)],
            TEAM_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, team_phone)],
            TEAM_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, team_role)],
        },
        fallbacks=[CommandHandler("cancel", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_reg)
    app.add_handler(conv_table)
    app.add_handler(conv_taxi)
    app.add_handler(conv_team)
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp))
    app.add_handler(CallbackQueryHandler(handle_button))

    print("🤖 Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
