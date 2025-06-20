# telegram_manager_bot.py (Cursor + .env friendly)

import os
import time
import threading
import json
import asyncio
from datetime import datetime
import schedule
from openai import OpenAI
from telethon.sync import TelegramClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from dotenv import load_dotenv

# === LOAD ENV VARS ===
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USER_ID = int(os.getenv("USER_ID"))

DATA_FILE = "data_store.json"
KEYWORDS = [
    "urgent", "invoice", "@yourname", "asap", "important", "reminder",
    "deadline", "follow up", "todo", "meeting", "action required", "payment",
    "feedback", "review", "blocker", "question", "help", "fix", "resolve"
]

openai_client = OpenAI(api_key=OPENAI_API_KEY)
telethon_client = TelegramClient("session", TELEGRAM_API_ID, TELEGRAM_API_HASH)

# === DATA FUNCTIONS ===
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"notes": [], "usage": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_note(text):
    data = load_data()
    data["notes"].append({"timestamp": datetime.now().isoformat(), "text": text})
    save_data(data)

def get_today_notes():
    data = load_data()
    today = datetime.now().date().isoformat()
    return [n for n in data["notes"] if today in n["timestamp"]]

def get_recent_notes(n=5):
    return load_data()["notes"][-n:]

def log_usage(usage):
    data = load_data()
    data["usage"].append({
        "timestamp": datetime.now().isoformat(),
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens
    })
    save_data(data)

# === OPENAI CHAT ===
def openai_chat(messages, temperature=0.6):
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=temperature
    )
    log_usage(response.usage)
    return response.choices[0].message.content

def summarize_messages(messages):
    text_block = "\n".join(messages)
    return openai_chat([
        {"role": "system", "content": "Summarize these chat messages and suggest follow-ups."},
        {"role": "user", "content": text_block}
    ])

def generate_text(prompt):
    return openai_chat([
        {"role": "system", "content": "You are a helpful assistant that writes professional messages."},
        {"role": "user", "content": prompt}
    ], temperature=0.7)

def generate_brief(notes, summaries):
    note_text = "\n".join([f"- {n['text']}" for n in notes]) or "No notes."
    chat_summary = "\n".join(summaries) or "No recent chat summaries."
    return openai_chat([
        {"role": "system", "content": "You generate clear, insightful daily briefings."},
        {"role": "user", "content": f"NOTES:\n{note_text}\n\nCHATS:\n{chat_summary}"}
    ])

# === TELEGRAM HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[
        InlineKeyboardButton("📋 Brief", callback_data="brief"),
        InlineKeyboardButton("📝 Note", callback_data="note")
    ], [
        InlineKeyboardButton("📊 Summary", callback_data="summary"),
        InlineKeyboardButton("📅 Follow-up", callback_data="followup")
    ], [
        InlineKeyboardButton("🧠 Generate", callback_data="generate"),
        InlineKeyboardButton("ℹ️ Help", callback_data="help")
    ]]
    await update.message.reply_text("Welcome! Choose a feature:", reply_markup=InlineKeyboardMarkup(buttons))

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "brief":
        await brief(update, context)
    elif query.data == "note":
        await context.bot.send_message(USER_ID, "Use /note <text> to save a note.")
    elif query.data == "summary":
        await summary(update, context)
    elif query.data == "followup":
        await followup(update, context)
    elif query.data == "generate":
        await context.bot.send_message(USER_ID, "Use /generate <prompt> to generate text.")
    elif query.data == "help":
        await context.bot.send_message(USER_ID,
            "/note <text> — Save a note\n"
            "/summary — View notes\n"
            "/followup — Tasks with 'todo', 'pending'\n"
            "/generate <prompt> — Write AI message\n"
            "/brief — Full AI-powered daily briefing\n"
        )

async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        return await context.bot.send_message(USER_ID, "⚠️ Usage: /note your text here")
    add_note(text)
    await context.bot.send_message(USER_ID, f"📝 Saved: {text}")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notes = get_recent_notes()
    if not notes:
        return await context.bot.send_message(USER_ID, "🧾 No notes yet.")
    await context.bot.send_message(USER_ID, "\n".join([f"{n['timestamp']}: {n['text']}" for n in notes]))

async def followup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notes = get_today_notes()
    action_items = [n for n in notes if any(kw in n["text"].lower() for kw in ["todo", "pending", "follow up"])]
    if not action_items:
        return await context.bot.send_message(USER_ID, "✅ No follow-ups today.")
    await context.bot.send_message(USER_ID, "\n".join([f"- {n['text']}" for n in action_items]))

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        return await context.bot.send_message(USER_ID, "⚠️ Usage: /generate your prompt")
    try:
        result = await asyncio.to_thread(generate_text, prompt)
        await context.bot.send_message(USER_ID, f"✍️ {result}")
    except Exception as e:
        await context.bot.send_message(USER_ID, f"❌ Error: {e}")

async def brief(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        def fetch_summary():
            telethon_client.start()
            chats = list(telethon_client.iter_dialogs())[:3]
            results = []
            for chat in chats:
                msgs = telethon_client.get_messages(chat.id, limit=20)
                texts = [m.message for m in msgs if m.message]
                results.append(summarize_messages(texts))
            telethon_client.disconnect()
            return results

        notes = get_today_notes()
        summaries = await asyncio.to_thread(fetch_summary)
        full_brief = await asyncio.to_thread(generate_brief, notes, summaries)
        await context.bot.send_message(USER_ID, f"📋 Your Daily Briefing:\n\n{full_brief}")
    except Exception as e:
        await context.bot.send_message(USER_ID, f"❌ Briefing failed: {e}")

async def keyword_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if any(k in text for k in KEYWORDS):
        await context.bot.send_message(USER_ID, f"🔔 Keyword detected:\n{text}")

# === SCHEDULER LOOP ===
def run_schedule(app):
    while True:
        schedule.run_pending()
        time.sleep(1)

# === MAIN ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("note", note))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("followup", followup))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("brief", brief))
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_filter))

    print("🤖 Bot is running...")
    threading.Thread(target=run_schedule, args=(app,), daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main() 