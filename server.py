import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7850448853:AAE5whRafwS-7Evy4Qs4NzqdSZ1dEQtgQh4"
ADMIN_ID = "1838192124"  # Твой ID
CHANNEL_ID = "-1002581582625"  # ID канала или группы (нужно с минусом и без @)

last_user_id = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот-пересыльщик сообщений.")

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_user_id
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text

    last_user_id = chat_id
    message_to_send = f"Сообщение от {user.first_name} (id: {chat_id}):\n{text}"

    await context.bot.send_message(chat_id=ADMIN_ID, text=message_to_send)

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_user_id
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Ты не админ, не могу выполнить.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Используй: /reply <user_id> <текст>")
        return

    try:
        user_id = int(args[0])
    except ValueError:
        await update.message.reply_text("Неверный user_id.")
        return

    reply_text = " ".join(args[1:])

    try:
        await context.bot.send_message(chat_id=user_id, text=reply_text)
        await update.message.reply_text(f"Отправлено пользователю {user_id}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при отправке: {e}")

async def sendchannel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Ты не админ, не могу выполнить.")
        return

    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Используй: /sendchannel <текст>")
        return

    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
        await update.message.reply_text("Сообщение отправлено в канал/группу.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при отправке: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply_command))
    app.add_handler(CommandHandler("sendchannel", sendchannel_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))

    app.run_polling()

if __name__ == "__main__":
    main()
