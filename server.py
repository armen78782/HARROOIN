import asyncio
import subprocess
import os
import nest_asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# Настройки
BOT_TOKEN = "7850448853:AAHoGKGwb4dHgs25RElSGE_LNHQBFv4zFiU"
ACCESS_PASSWORD = "osint123"
AUTHORIZED_USERS = set()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        await show_menu(update)
    else:
        await update.message.reply_text("Введите пароль для доступа:")

# Проверка пароля
async def password_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        return

    if update.message.text == ACCESS_PASSWORD:
        AUTHORIZED_USERS.add(user_id)
        await update.message.reply_text("Доступ разрешён!")
        await show_menu(update)
    else:
        await update.message.reply_text("Неверный пароль.")

# Главное меню
async def show_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("Поиск username (Sherlock)", callback_data='sherlock')],
        [InlineKeyboardButton("Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери команду:", reply_markup=reply_markup)

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in AUTHORIZED_USERS:
        await query.edit_message_text("Сначала авторизуйся через /start.")
        return

    if query.data == "help":
        await query.edit_message_text("OSINT бот:\n- Ищи username через Sherlock\n- Команды будут добавлены позже.")
    elif query.data == "sherlock":
        context.user_data["action"] = "sherlock"
        await query.edit_message_text("Введи username для поиска через Sherlock:")

# Обработка сообщений после выбора действия
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("Сначала авторизуйся через /start.")
        return

    action = context.user_data.get("action")

    if action == "sherlock":
        username = update.message.text.strip()
        await update.message.reply_text(f"Ищу {username} через Sherlock, подожди...")

        output_file = f"sherlock_{username}.txt"
        cmd = ["python3", "sherlock/sherlock.py", username, "--print-found", "--timeout", "5"]

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
            found = [line for line in result.stdout.split("\n") if line.startswith("[+]")]

            if found:
                with open(output_file, "w") as f:
                    f.write("\n".join(found))
                await update.message.reply_document(document=open(output_file, "rb"))
                os.remove(output_file)
            else:
                await update.message.reply_text("Профили не найдены.")
        except Exception as e:
            await update.message.reply_text(f"Ошибка при запуске Sherlock:\n{e}")

        context.user_data["action"] = None
    else:
        await update.message.reply_text("Используй /start для начала.")

# Основной запуск
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, password_check))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("OSINT бот запущен.")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
