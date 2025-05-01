from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json

with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['TOKEN']

app = ApplicationBuilder().token(TOKEN).build()

async def get_chat_id(update, context):
    chat_id = update.message.chat_id
    print(chat_id)
    await update.message.reply_text(f"你的chat_id是：{chat_id}")

app.add_handler(CommandHandler("start", get_chat_id))

print("Bot启动了...")
app.run_polling()