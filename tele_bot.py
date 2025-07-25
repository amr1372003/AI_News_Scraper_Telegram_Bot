import json
import pandas as pd
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = '...................YOUR BOT TOKEN...................'
KEYWORDS_FILE = "users_keywords.json"

# ---------- Helper Functions ----------
def get_user_keywords(user_id):
    data = load_keywords()
    return [kw.lower() for kw in data.get(str(user_id), [])]

def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        return {}
    with open(KEYWORDS_FILE, "r") as file:
        return json.load(file)

def save_keywords(data):
    with open(KEYWORDS_FILE, "w") as file:
        json.dump(data, file, indent=4)

# ---------- Keyword Functions ----------

async def set_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    text = update.message.text
    new_keywords = [kw.strip().lower() for kw in text.split(',') if kw.strip()]
    
    if not new_keywords:
        await update.message.reply_text("❌ Please provide valid keywords separated by commas.")
        return

    data = load_keywords()
    data.setdefault(chat_id, [])
    data[chat_id].extend(new_keywords)
    data[chat_id] = list(set(data[chat_id]))  # remove duplicates
    save_keywords(data)

    await update.message.reply_text(f"✅ Keywords updated:\n{', '.join(data[chat_id])}")

async def view_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    data = load_keywords()
    keywords = data.get(chat_id, [])

    if not keywords:
        await update.message.reply_text("📭 You haven't set any keywords yet.")
    else:
        await update.message.reply_text(f"📌 Your keywords:\n{', '.join(keywords)}")

async def delete_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    data = load_keywords()

    if chat_id not in data or not data[chat_id]:
        await update.message.reply_text("🗑️ No keywords to delete.")
        return

    text = update.message.text.strip().lower()
    args = [arg.strip() for arg in text.split()]

    if len(args) == 1:
        # Delete all
        data[chat_id] = []
        save_keywords(data)
        await update.message.reply_text("🗑️ All keywords deleted.")
    else:
        # Delete specific keywords
        to_delete = set(args[1:])
        original = set(data[chat_id])
        updated = list(original - to_delete)

        data[chat_id] = updated
        save_keywords(data)
        await update.message.reply_text(f"✅ Remaining keywords:\n{', '.join(updated)}")


# ---------- send news to users based on keywords ----------
async def send_relevant_news(bot, user_id, csv_path="news_data.csv"):
    user_keywords = get_user_keywords(user_id)
    if not user_keywords:
        await bot.send_message(chat_id=user_id, text="⚠️ You haven't set any keywords yet.")
        return

    if not os.path.exists(csv_path):
        await bot.send_message(chat_id=user_id, text="❌ News file not found.")
        return

    df = pd.read_csv(csv_path)
    matches = []

    for _, row in df.iterrows():
        content = f"{row['title']} {row['content_summary']}".lower()
        score = sum(1 for kw in user_keywords if kw in content)
        if score >= 2:
            matches.append(row)

    if not matches:
        await bot.send_message(chat_id=user_id, text="🔍 No relevant news found for your keywords.")
        return

    for row in matches[:]:  # just send all results
        message = (
                f"*title:* {row['title']}\n\n"
                f"*Summary:* {row['content_summary']}\n"
                f"[Read More]({row['link']})\n\n"
                f"*Published:* {row['date']}\n\n"
                f"*Author:* {row['author']}"
            )

        await bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown", disable_web_page_preview=False)

# ---------- Start & Main ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n"
        "You can set your keywords by sending them as a comma-separated list.\n"
        "For example: keyword1, keyword2\n"
        "Use /mykeywords to view your keywords.\n"
        "Use /removekeywords to delete your keywords.\n"
    )


async def handle_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    await send_relevant_news(context.bot, user_id)


# ---------- Setup Bot ----------

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mykeywords", view_keywords))
    app.add_handler(CommandHandler("removekeywords", delete_keywords))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_keywords))
    app.add_handler(CommandHandler("news", handle_news))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
