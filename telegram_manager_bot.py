# telegram_manager_bot.py (Cursor + .env friendly)

import os
import time
import threading
import json
import asyncio
from datetime import datetime
import schedule
from openai import OpenAI
from telethon import TelegramClient
import requests
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
SUI_NODE_URL = os.getenv("SUI_NODE_URL")
SUI_PACKAGE = os.getenv("SUI_PACKAGE")
SUI_MODULE = os.getenv("SUI_MODULE")

DATA_FILE = "data_store.json"
KEYWORDS = [
    "urgent", "invoice", "@yourname", "asap", "important", "reminder",
    "deadline", "follow up", "todo", "meeting", "action required", "payment",
    "feedback", "review", "blocker", "question", "help", "fix", "resolve"
]

openai_client = OpenAI(api_key=OPENAI_API_KEY)
sui_cursor = None

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

async def read_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send recent messages from all chats."""
    try:
        async with TelegramClient("session", TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
            dialogs = []
            async for dialog in client.iter_dialogs():
                dialogs.append(dialog)

            lines = []
            for dialog in dialogs:
                msgs = await client.get_messages(dialog.id, limit=50)
                for msg in reversed(msgs):
                    if msg.message:
                        sender = msg.sender_id
                        lines.append(f"[{dialog.name}] {sender}: {msg.message}")

            if not lines:
                return await context.bot.send_message(USER_ID, "No messages found.")

            text = "\n".join(lines)
            if len(text) > 4000:
                with open("all_messages.txt", "w") as f:
                    f.write(text)
                await context.bot.send_document(USER_ID, document="all_messages.txt")
                os.remove("all_messages.txt")
            else:
                await context.bot.send_message(USER_ID, text)
    except Exception as e:
        await context.bot.send_message(USER_ID, f"❌ Error fetching messages: {e}")

async def brief(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async def fetch_summary():
            async with TelegramClient("session", TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
                chats = []
                async for dialog in client.iter_dialogs():
                    chats.append(dialog)
                    if len(chats) >= 3:
                        break

                results = []
                for chat in chats:
                    msgs = await client.get_messages(chat.id, limit=20)
                    texts = [m.message for m in msgs if m.message]
                    summary = await asyncio.to_thread(summarize_messages, texts)
                    results.append(summary)
                return results

        notes = get_today_notes()
        summaries = await fetch_summary()
        full_brief = await asyncio.to_thread(generate_brief, notes, summaries)
        await context.bot.send_message(USER_ID, f"📋 Your Daily Briefing:\n\n{full_brief}")
    except Exception as e:
        await context.bot.send_message(USER_ID, f"❌ Briefing failed: {e}")

async def keyword_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if any(k in text for k in KEYWORDS):
        await context.bot.send_message(USER_ID, f"🔔 Keyword detected:\n{text}")

async def check_sui_events(app):
    """Poll Sui RPC for events from the configured contract."""
    global sui_cursor
    if not SUI_NODE_URL or not SUI_PACKAGE or not SUI_MODULE:
        return
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "suix_queryEvents",
            "params": [
                {"MoveEventModule": {"package": SUI_PACKAGE, "module": SUI_MODULE}},
                sui_cursor,
                10,
                False,
            ],
        }
        r = requests.post(SUI_NODE_URL, json=payload, timeout=10)
        r.raise_for_status()
        res = r.json().get("result", {})
        events = res.get("data", [])
        if events:
            sui_cursor = res.get("nextCursor")
            for ev in events:
                await app.bot.send_message(USER_ID, f"📣 Sui event detected:\n{ev}")
    except Exception as e:
        print("Sui check failed", e)

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
    app.add_handler(CommandHandler("readall", read_all))
    app.add_handler(CommandHandler("brief", brief))
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_filter))

    schedule.every(60).seconds.do(lambda: asyncio.run(check_sui_events(app)))

    print("🤖 Bot is running...")
    threading.Thread(target=run_schedule, args=(app,), daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main() 