import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "7850448853:AAHoGKGwb4dHgs25RElSGE_LNHQBFv4zFiU"
ACCESS_PASSWORD = "osint123"
AUTHORIZED_USERS = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        await update.message.reply_text("Ты уже авторизован. Введи /help.")
    else:
        await update.message.reply_text("Введи пароль:")

async def password_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        return

    if update.message.text == ACCESS_PASSWORD:
        AUTHORIZED_USERS.add(user_id)
        await update.message.reply_text("Доступ разрешён! Введи /help.")
    else:
        await update.message.reply_text("Неверный пароль. Попробуй снова.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Сначала введи пароль через /start.")
        return

    await update.message.reply_text("""
Команды OSINT:
- /email someone@example.com
(добавим позже другие)
""")

async def email_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Сначала введи пароль через /start.")
        return

    if not context.args:
        await update.message.reply_text("Пример: /email test@example.com")
        return

    email = context.args[0]
    await update.message.reply_text(f"Ищем информацию по email: {email} (пока заглушка)")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("email", email_search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, password_check))

    print("Бот запущен.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
