import sys
sys.path.insert(0, "/home/ispasatel/www/kosse_bot/site-packages")  # путь на сервере (можно убрать на Railway)
import os
from telegram import (
    Update, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

print("🚀 Запускается новый код Kosse Bot!")

CHOOSE_ACTION, ASK_QUESTION, BUY_TICKET, CHOOSE_EVENT_FOR_QUESTION = range(4)

organizer_contact = "@kosse_club"

ABOUT_TEXT = (
    "Kosse.club — это турбаза «Кемпинг зона», созданная для проведения мероприятий семейного и бизнес-формата.\n\n"
    "Мы предлагаем:\n"
    "• 👨‍👩‍👧‍👦 Семейные праздники — свадьбы, дни рождения, аренда территории для личных мероприятий.\n"
    "• 🏢 Корпоративные форматы — майсы, ивенты, тимбилдинги, ретриты.\n"
    "• 🎯 Развлечения и активный отдых — пейнтбол, командные игры («Крокодил», «Битва Героев»).\n"
    "• 🍷 Гастрономические программы — дегустации вин и других напитков, сомелье сессии.\n"
    "• 🎨 Творческие мастер-классы — лепка, керамика, создание трендовых игрушек и изделий.\n\n"
    "У нас вы найдёте всё для яркого отдыха и сплочения команды — от душевных семейных торжеств до масштабных корпоративных событий."
)

ABOUT_PHOTO = "https://raw.githubusercontent.com/EV4557/KOSSE.club---bot/main/logoKosse.png"

# Главное меню
main_menu = ReplyKeyboardMarkup([
    ["Контакты", "Ближайшие мероприятия"],
    ["Немного о нас", "Дресс-код и правила посещения"],
    ["Задать вопрос", "Купить билет"]
], resize_keyboard=True)

# Мероприятия
EVENTS = {
    "Хоровод Света": {
        "ссылка": "https://kaliningrad.qtickets.events/183804-khorovod-sveta",
        "цена": "🎟️ Дети с 4-12 — 700₽\n💎 Стандартный — 1000₽\n🎩 Все включено — 1400₽",
        "время": "🕖 13 сентября\nНачало в 13:00, окончание в 22:00",
        "место": "📍 Кемпинг Kosse.club, ул. Советская, 10, Янтарный."
    }
}

# Ключевые слова
PRICE_KEYWORDS = ["цена", "цен", "стоимость", "сколько стоит", "билет", "прайс", "оплата", "денег", "руб", "₽"]
TIME_KEYWORDS = ["время", "времен", "когда", "во сколько", "расписание", "дата", "число", "сроки", "день", "начало", "окончание"]
PLACE_KEYWORDS = ["место", "мест", "где", "адрес", "локация", "территория", "площадка", "кемпинг", "kosse", "kosse.club", "как добраться"]
RETURN_KEYWORDS = ["возврат", "вернуть", "обмен", "refund", "отмена", "отменить", "сдать билет", "вернуть деньги"]
CONTACT_KEYWORDS = ["контакт", "связь", "телефон", "почта", "email", "организатор", "поддержка", "админ"]
ABOUT_KEYWORDS = ["о вас", "о клубе", "о нас", "инфо", "информация", "что такое kosse", "немного о вас", "чем занимаетесь"]

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот Kosse.club 🎟️\nВыберите, что вас интересует:",
        reply_markup=main_menu
    )
    return CHOOSE_ACTION

async def handle_faq_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_clean = update.message.text.strip().lower()

    if text_clean in ["цена", "время", "место"]:
        context.user_data["faq_type"] = text_clean
        keyboard = [[name] for name in EVENTS.keys()] + [["⬅ Назад"]]
        await update.message.reply_text(
            "Выберите мероприятие, про которое хотите узнать:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return CHOOSE_EVENT_FOR_QUESTION

    elif text_clean == "возврат билета":
        await update.message.reply_text(
            f"🧾 Для оформления возврата билета напишите на {organizer_contact} и укажите необходимую информацию.",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION

    elif text_clean == "⬅ назад":
        await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

    else:
        await update.message.reply_text("Пожалуйста, выберите вариант из меню.")
        return ASK_QUESTION

async def handle_faq_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

    faq_type = context.user_data.get("faq_type")
    event_info = EVENTS.get(text)

    if not event_info:
        await update.message.reply_text("Пожалуйста, выберите мероприятие из списка.")
        return CHOOSE_EVENT_FOR_QUESTION

    if faq_type == "цена":
        msg = f"Цена на {text}:\n{event_info.get('цена', 'Цены уточняются.')}"
    elif faq_type == "время":
        msg = f"Время проведения {text}:\n{event_info.get('время', 'Время уточняется.')}"
    elif faq_type == "место":
        msg = f"Место проведения {text}:\n{event_info.get('место', 'Место уточняется.')}"
    else:
        msg = "Информация недоступна."

    await update.message.reply_text(msg, reply_markup=main_menu)
    context.user_data.pop("faq_type", None)
    return CHOOSE_ACTION

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_clean = update.message.text.strip().lower()

    if text_clean == "купить билет":
        keyboard = [[event] for event in EVENTS.keys()] + [["⬅ Назад"]]
        await update.message.reply_text(
            "Выберите мероприятие для покупки билета:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return BUY_TICKET

    elif any(word in text_clean for word in CONTACT_KEYWORDS):
        await update.message.reply_text(f"📞 Свяжитесь с организатором:\n{organizer_contact}", reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text_clean == "ближайшие мероприятия":
        for name, info in EVENTS.items():
            message = f"🎉 {name}\n{info.get('время','')}\n{info.get('место','')}"
            keyboard = [[InlineKeyboardButton("Купить билет", url=info['ссылка'])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(message, reply_markup=reply_markup)
        return CHOOSE_ACTION

    elif text_clean == "немного о нас":
        await update.message.reply_photo(photo=ABOUT_PHOTO, caption="Проект Kosse.club 👇", reply_markup=main_menu)
        await update.message.reply_text(ABOUT_TEXT, reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text_clean == "дресс-код и правила посещения":
        rules = (
            "🎟️ *Правила посещения и дресс-код:*\n\n"
            "1️⃣ Вход только с билетом.\n"
            "2️⃣ Личный документ.\n"
            "3️⃣ Нарушители могут быть удалены.\n\n"
            "🙏 Спасибо за понимание!"
        )
        await update.message.reply_text(rules, parse_mode="Markdown", reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text_clean == "задать вопрос":
        keyboard = [["Цена", "Время", "Место", "Возврат билета"], ["⬅ Назад"]]
        await update.message.reply_text("❓ Часто задаваемые вопросы:\nВыберите категорию:",
                                        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        context.user_data["fail_count"] = 0
        return ASK_QUESTION

    elif any(word in text_clean for word in PRICE_KEYWORDS + TIME_KEYWORDS + PLACE_KEYWORDS + RETURN_KEYWORDS + ABOUT_KEYWORDS):
        return await handle_faq_question(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите вариант из меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

async def handle_buy_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

    if text in EVENTS:
        await update.message.reply_text(f"🎫 Ссылка для покупки билета:\n{EVENTS[text]['ссылка']}", reply_markup=main_menu)
        return CHOOSE_ACTION
    else:
        await update.message.reply_text("Пожалуйста, выберите мероприятие из списка.")
        return BUY_TICKET

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
    return CHOOSE_ACTION

# --- Запуск бота ---
def main():
    # Получаем токен из переменной окружения
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ Ошибка: не задан BOT_TOKEN в переменных окружения!")
        return

    app = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_action)],
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_faq_question)],
            CHOOSE_EVENT_FOR_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_faq_event)],
            BUY_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buy_ticket)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("🚀 Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()