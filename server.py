from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Настройки
BOT_TOKEN = "ТВОЙ_ТОКЕН_ЗДЕСЬ"
ACCESS_PASSWORD = "osint123"  # Пароль для подключения
AUTHORIZED_USERS = set()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        await update.message.reply_text("Ты уже авторизован. Используй /help.")
    else:
        await update.message.reply_text("Введите пароль для доступа:")

# Обработка пароля
async def password_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        return

    if update.message.text == ACCESS_PASSWORD:
        AUTHORIZED_USERS.add(user_id)
        await update.message.reply_text("Доступ разрешён! Используй /help для команд.")
    else:
        await update.message.reply_text("Неверный пароль. Попробуй снова.")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Сначала введи пароль через /start.")
        return

    help_text = """
OSINT команды:
- /email <email> — поиск по email
- /username <ник> — поиск по соцсетям
- /ip <ip-адрес> — информация об IP
"""
    await update.message.reply_text(help_text)

# Пример команды — поиск email
async def email_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Сначала введи пароль через /start.")
        return

    if not context.args:
        await update.message.reply_text("Пример: /email someone@example.com")
        return

    email = context.args[0]
    # Заглушка — сюда можно вставить реальные API-запросы
    await update.message.reply_text(f"Поиск информации по email: {email}\n(Тут будет результат)")

# Основной запуск
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("email", email_search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, password_check))

    print("Бот запущен...")
    app.run_polling()
