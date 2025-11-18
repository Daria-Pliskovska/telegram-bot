import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== НАЛАШТУВАННЯ ==========
# ВАЖЛИВО: Замініть на ваш токен від @BotFather
BOT_TOKEN = "8410976877:AAFsHwlWSOrI4iy7b_XHR2_qp64tIvFCHbs"

# ID адміністраторів (ваш Telegram ID)
# Щоб дізнатися свій ID, напишіть боту @userinfobot
ADMIN_IDS = [1443083195, 1196829928]  # Замініть на ваші ID

# Стани розмови
CHOOSING, WAITING_CONTENT = range(2)

# ========== ФУНКЦІЇ БОТА ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник команди /start"""
    user = update.effective_user
    
    # Привітання
    keyboard = [
        [KeyboardButton("👋 Привіт")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        f"Вітаю, {user.first_name}! 👋\n\n"
        "Цей бот створений для збору фото, відео та історій.\n"
        "Натисніть кнопку нижче, щоб почати! 👇"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return CHOOSING


async def greeting_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник привітання"""
    keyboard = [
        [InlineKeyboardButton("📷 Фото", callback_data="photo")],
        [InlineKeyboardButton("🎥 Відео", callback_data="video")],
        [InlineKeyboardButton("📷🎥 Обидва варіанти", callback_data="both")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "Привіт! Що ти хочеш мені розповісти/показати?"
    
    await update.message.reply_text(text, reply_markup=reply_markup)
    return WAITING_CONTENT


async def choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник вибору типу контенту"""
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    context.user_data['choice'] = choice
    
    # Видаляємо стару клавіатуру
    keyboard = [[KeyboardButton("🔙 Повернутися на початок")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if choice == "photo":
        text = "📷 Відмінно! Надішліть мені фото.\nВи також можете додати підпис до фото."
    elif choice == "video":
        text = "🎥 Чудово! Надішліть мені відео.\nВи також можете додати підпис до відео."
    else:  # both
        text = "📷🎥 Супер! Надішліть мені фото або відео.\nВи можете надіслати декілька файлів.\nТакож можете додати підпис."
    
    await query.edit_message_text(text)
    await query.message.reply_text("Чекаю на ваш контент...", reply_markup=reply_markup)
    
    return WAITING_CONTENT


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник фото"""
    user = update.effective_user
    photo = update.message.photo[-1]  # Отримуємо найбільше фото
    caption = update.message.caption or "Без підпису"
    
    # Відправка адміністраторам
    for admin_id in ADMIN_IDS:
        try:
            admin_text = (
                f"📷 НОВЕ ФОТО\n\n"
                f"👤 Від: {user.first_name} {user.last_name or ''}\n"
                f"🆔 User ID: {user.id}\n"
                f"👤 Username: @{user.username or 'немає'}\n"
                f"💬 Підпис: {caption}\n"
            )
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=photo.file_id,
                caption=admin_text
            )
        except Exception as e:
            logger.error(f"Помилка відправки фото адміну {admin_id}: {e}")
    
    # Підтвердження користувачу
    await update.message.reply_text(
        "✅ Дякую! Ваше фото успішно надіслано.\n\n"
        "Можете надіслати ще контент або повернутися на початок."
    )
    
    return WAITING_CONTENT


async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник відео"""
    user = update.effective_user
    video = update.message.video
    caption = update.message.caption or "Без підпису"
    
    # Відправка адміністраторам
    for admin_id in ADMIN_IDS:
        try:
            admin_text = (
                f"🎥 НОВЕ ВІДЕО\n\n"
                f"👤 Від: {user.first_name} {user.last_name or ''}\n"
                f"🆔 User ID: {user.id}\n"
                f"👤 Username: @{user.username or 'немає'}\n"
                f"💬 Підпис: {caption}\n"
            )
            await context.bot.send_video(
                chat_id=admin_id,
                video=video.file_id,
                caption=admin_text
            )
        except Exception as e:
            logger.error(f"Помилка відправки відео адміну {admin_id}: {e}")
    
    # Підтвердження користувачу
    await update.message.reply_text(
        "✅ Дякую! Ваше відео успішно надіслано.\n\n"
        "Можете надіслати ще контент або повернутися на початок."
    )
    
    return WAITING_CONTENT


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник текстових повідомлень"""
    user = update.effective_user
    text = update.message.text
    
    if text == "🔙 Повернутися на початок":
        return await start(update, context)
    
    # Відправка текстового повідомлення адміністраторам
    for admin_id in ADMIN_IDS:
        try:
            admin_text = (
                f"💬 НОВЕ ТЕКСТОВЕ ПОВІДОМЛЕННЯ\n\n"
                f"👤 Від: {user.first_name} {user.last_name or ''}\n"
                f"🆔 User ID: {user.id}\n"
                f"👤 Username: @{user.username or 'немає'}\n\n"
                f"📝 Повідомлення:\n{text}\n"
            )
            await context.bot.send_message(chat_id=admin_id, text=admin_text)
        except Exception as e:
            logger.error(f"Помилка відправки тексту адміну {admin_id}: {e}")
    
    # Підтвердження користувачу
    await update.message.reply_text(
        "✅ Дякую! Ваше повідомлення успішно надіслано.\n\n"
        "Можете надіслати ще контент або повернутися на початок."
    )
    
    return WAITING_CONTENT


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник документів"""
    user = update.effective_user
    document = update.message.document
    caption = update.message.caption or "Без підпису"
    
    # Відправка адміністраторам
    for admin_id in ADMIN_IDS:
        try:
            admin_text = (
                f"📎 НОВИЙ ДОКУМЕНТ\n\n"
                f"👤 Від: {user.first_name} {user.last_name or ''}\n"
                f"🆔 User ID: {user.id}\n"
                f"👤 Username: @{user.username or 'немає'}\n"
                f"📄 Файл: {document.file_name}\n"
                f"💬 Підпис: {caption}\n"
            )
            await context.bot.send_document(
                chat_id=admin_id,
                document=document.file_id,
                caption=admin_text
            )
        except Exception as e:
            logger.error(f"Помилка відправки документу адміну {admin_id}: {e}")
    
    # Підтвердження користувачу
    await update.message.reply_text(
        "✅ Дякую! Ваш файл успішно надіслано.\n\n"
        "Можете надіслати ще контент або повернутися на початок."
    )
    
    return WAITING_CONTENT


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скасування розмови"""
    await update.message.reply_text(
        "Дякую за використання бота! До зустрічі! 👋"
    )
    return ConversationHandler.END


# ========== КОМАНДИ ДЛЯ АДМІНІСТРАТОРА ==========

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика для адміністратора"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас немає доступу до цієї команди.")
        return
    
    stats_text = (
        "📊 СТАТИСТИКА БОТА\n\n"
        f"🤖 Бот активний\n"
        f"👥 Адміністраторів: {len(ADMIN_IDS)}\n"
    )
    
    await update.message.reply_text(stats_text)


async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Довідка для адміністратора"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас немає доступу до цієї команди.")
        return
    
    help_text = (
        "🔧 КОМАНДИ АДМІНІСТРАТОРА\n\n"
        "/start - Запустити бота\n"
        "/stats - Показати статистику\n"
        "/help - Ця довідка\n"
        "/cancel - Скасувати поточну дію\n\n"
        "Всі надіслані фото, відео та повідомлення будуть автоматично надходити вам."
    )
    
    await update.message.reply_text(help_text)


def main():
    """Запуск бота"""
    # Створення Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ConversationHandler для обробки діалогу
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^👋 Привіт$"), greeting_handler),
            ],
            WAITING_CONTENT: [
                CallbackQueryHandler(choice_handler),
                MessageHandler(filters.PHOTO, photo_handler),
                MessageHandler(filters.VIDEO, video_handler),
                MessageHandler(filters.Document.ALL, document_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Додавання обробників
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("stats", admin_stats))
    application.add_handler(CommandHandler("help", admin_help))
    
    # Запуск бота
    logger.info("Бот запущено!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
