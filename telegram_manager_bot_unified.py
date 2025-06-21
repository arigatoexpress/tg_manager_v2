# telegram_manager_bot_unified.py
"""
Telegram Manager Bot with Unified AI Backend
--------------------------------------------
This bot can use either local Ollama models or Atoma DePIN network for AI processing.

Commands:
  /start - show menu
  /note <text> - save a note
  /summary - recent notes
  /followup - today's tasks
  /generate <prompt> - AI text
  /brief - daily briefing
  /meeting [topic] - create meeting link
  /readall - dump messages
  /leads - sync chat summaries to Google Sheets
  /ai_status - check AI backend status
"""

import os
import time
import threading
import json
import asyncio
from datetime import datetime
import schedule
import secrets
import requests
import gspread
from google.oauth2.service_account import Credentials
from telethon import TelegramClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from dotenv import load_dotenv

# Import our AI clients
from ollama_client import initialize_ollama_client, get_ollama_client
from atoma_client import initialize_atoma_client, get_atoma_client

# === LOAD ENV VARS ===
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
USER_ID = int(os.getenv("USER_ID"))
SUI_NODE_URL = os.getenv("SUI_NODE_URL")
SUI_PACKAGE = os.getenv("SUI_PACKAGE")
SUI_MODULE = os.getenv("SUI_MODULE")

MEETING_URL_BASE = os.getenv("MEETING_URL_BASE", "https://meet.jit.si")
CONTEXT_FILE = os.getenv("CONTEXT_FILE", "context.md")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")

# AI Backend Configuration
AI_BACKEND = os.getenv("AI_BACKEND", "ollama").lower()  # "ollama" or "atoma"

DATA_FILE = "data_store.json"
KEYWORDS = [
    "urgent", "invoice", "@yourname", "asap", "important", "reminder",
    "deadline", "follow up", "todo", "meeting", "action required", "payment",
    "feedback", "review", "blocker", "question", "help", "fix", "resolve"
]

# Initialize AI backend
ai_client = None
ai_backend_name = "Unknown"

def initialize_ai_backend():
    """Initialize the appropriate AI backend based on configuration"""
    global ai_client, ai_backend_name
    
    print(f"🤖 Initializing AI backend: {AI_BACKEND}")
    
    if AI_BACKEND == "atoma":
        try:
            initialize_atoma_client()
            ai_client = get_atoma_client()
            ai_backend_name = "Atoma DePIN Network"
            print("✅ Atoma DePIN network initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Atoma: {e}")
            print("🔄 Falling back to Ollama...")
            AI_BACKEND = "ollama"
    
    if AI_BACKEND == "ollama":
        try:
            initialize_ollama_client()
            ai_client = get_ollama_client()
            ai_backend_name = "Local Ollama"
            print("✅ Ollama initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Ollama: {e}")
            raise Exception("No AI backend available")

# Initialize AI backend
try:
    initialize_ai_backend()
except Exception as e:
    print(f"❌ AI backend initialization failed: {e}")
    print("Please check your configuration and ensure either Ollama or Atoma is available")
    exit(1)

def load_context():
    """Load custom context from file if available."""
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r") as f:
            return f.read().strip()
    return ""

GPT_CONTEXT = load_context()
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
        "backend": ai_backend_name,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens
    })
    save_data(data)

# === UNIFIED AI CHAT ===
def ai_chat(messages, temperature=0.6):
    """Chat with the configured AI backend"""
    if GPT_CONTEXT:
        messages = [{"role": "system", "content": GPT_CONTEXT}] + messages
    
    try:
        response = ai_client.chat_completions_create(
            messages=messages,
            temperature=temperature
        )
        log_usage(response.usage)
        return response.choices[0].message["content"]
    except Exception as e:
        print(f"Error in AI chat ({ai_backend_name}): {e}")
        return f"Sorry, I encountered an error with {ai_backend_name}: {str(e)}"

def summarize_messages(messages):
    text_block = "\n".join(messages)
    return ai_chat(
        [
            {"role": "system", "content": "Summarize these chat messages and suggest follow-ups."},
            {"role": "user", "content": text_block}
        ]
    )

def generate_text(prompt):
    return ai_chat(
        [
            {"role": "system", "content": "You are a helpful assistant that writes professional messages."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

def generate_brief(notes, summaries):
    note_text = "\n".join([f"- {n['text']}" for n in notes]) or "No notes."
    chat_summary = "\n".join(summaries) or "No recent chat summaries."
    return ai_chat(
        [
            {"role": "system", "content": "You generate clear, insightful daily briefings."},
            {"role": "user", "content": f"NOTES:\n{note_text}\n\nCHATS:\n{chat_summary}"},
        ]
    )

def generate_meeting_link():
    """Create a unique meeting link using the configured base URL."""
    token = secrets.token_urlsafe(8)
    return f"{MEETING_URL_BASE.rstrip('/')}/{token}"

# === GOOGLE SHEETS INTEGRATION ===
def get_sheet():
    """Return the Google Sheet client if configured."""
    if not GOOGLE_SERVICE_ACCOUNT_FILE or not GOOGLE_SPREADSHEET_ID:
        raise RuntimeError("Google Sheets not configured")
    creds = Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    client = gspread.authorize(creds)
    return client.open_by_key(GOOGLE_SPREADSHEET_ID).sheet1

async def collect_contact_data():
    """Gather message summaries and follow-up suggestions for each chat."""
    results = []
    async with TelegramClient("session", TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        async for dialog in client.iter_dialogs():
            try:
                msgs = await client.get_messages(dialog.id, limit=50)
                texts = [m.message for m in msgs if m.message]
                if not texts:
                    continue
                summary = await asyncio.to_thread(summarize_messages, texts)
                follow = await asyncio.to_thread(
                    ai_chat,
                    [
                        {
                            "role": "system",
                            "content": (
                                "You are a business development assistant for a Sui DeFi startup. "
                                "Based on this chat history, summarize the deal progress and suggest next actions."
                            ),
                        },
                        {"role": "user", "content": "\n".join(texts)},
                    ],
                )
                last_date = msgs[0].date.strftime("%Y-%m-%d") if msgs else ""
                results.append(
                    {
                        "contact": dialog.name,
                        "last": last_date,
                        "summary": summary,
                        "follow": follow,
                    }
                )
            except Exception as e:
                print("collect_contact_data failed", dialog.name, e)
    return results

def update_sheet(rows):
    """Update Google Sheet with contact data."""
    sheet = get_sheet()
    sheet.clear()
    sheet.append_row(["Contact", "Last Contact", "Summary", "Follow-up"])
    for row in rows:
        sheet.append_row([row["contact"], row["last"], row["summary"], row["follow"]])

async def sync_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sync chat summaries to Google Sheets."""
    if update.effective_user.id != USER_ID:
        return
    await update.message.reply_text("🔄 Syncing to Google Sheets...")
    try:
        rows = await collect_contact_data()
        update_sheet(rows)
        await update.message.reply_text(f"✅ Synced {len(rows)} contacts to Google Sheets")
    except Exception as e:
        await update.message.reply_text(f"❌ Sync failed: {e}")

# === TELEGRAM BOT HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if update.effective_user.id != USER_ID:
        return
    
    keyboard = [
        [InlineKeyboardButton("📝 Add Note", callback_data="note")],
        [InlineKeyboardButton("📊 Summary", callback_data="summary")],
        [InlineKeyboardButton("✅ Follow-up", callback_data="followup")],
        [InlineKeyboardButton("🤖 Generate", callback_data="generate")],
        [InlineKeyboardButton("📅 Brief", callback_data="brief")],
        [InlineKeyboardButton("🔗 Meeting", callback_data="meeting")],
        [InlineKeyboardButton("📋 Read All", callback_data="readall")],
        [InlineKeyboardButton("📈 Leads", callback_data="leads")],
        [InlineKeyboardButton("🤖 AI Status", callback_data="ai_status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🤖 **Telegram Manager Bot**\n\n"
        f"**AI Backend:** {ai_backend_name}\n"
        f"Choose an action:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu button callbacks"""
    if update.effective_user.id != USER_ID:
        return
    
    query = update.callback_query
    await query.answer()
    
    if query.data == "note":
        await query.edit_message_text(
            "📝 **Add Note**\n\n"
            "Use: `/note <your note text>`\n\n"
            "Example: `/note Meeting with John tomorrow at 2pm`",
            parse_mode='Markdown'
        )
    elif query.data == "summary":
        await query.edit_message_text(
            "📊 **Recent Notes**\n\n"
            "Use: `/summary` to see recent notes",
            parse_mode='Markdown'
        )
    elif query.data == "followup":
        await query.edit_message_text(
            "✅ **Today's Follow-ups**\n\n"
            "Use: `/followup` to see today's tasks",
            parse_mode='Markdown'
        )
    elif query.data == "generate":
        await query.edit_message_text(
            "🤖 **Generate Text**\n\n"
            "Use: `/generate <prompt>`\n\n"
            "Example: `/generate Write a professional email to schedule a meeting`",
            parse_mode='Markdown'
        )
    elif query.data == "brief":
        await query.edit_message_text(
            "📅 **Daily Briefing**\n\n"
            "Use: `/brief` to get AI-generated daily briefing",
            parse_mode='Markdown'
        )
    elif query.data == "meeting":
        await query.edit_message_text(
            "🔗 **Meeting Link**\n\n"
            "Use: `/meeting [topic]` to generate a meeting link",
            parse_mode='Markdown'
        )
    elif query.data == "readall":
        await query.edit_message_text(
            "📋 **Read All Messages**\n\n"
            "Use: `/readall` to dump recent messages",
            parse_mode='Markdown'
        )
    elif query.data == "leads":
        await query.edit_message_text(
            "📈 **Sync Leads**\n\n"
            "Use: `/leads` to sync chat summaries to Google Sheets",
            parse_mode='Markdown'
        )
    elif query.data == "ai_status":
        await query.edit_message_text(
            f"🤖 **AI Backend Status**\n\n"
            f"**Backend:** {ai_backend_name}\n"
            f"**Status:** ✅ Active\n"
            f"**Model:** {ai_client.model if hasattr(ai_client, 'model') else 'Unknown'}",
            parse_mode='Markdown'
        )

async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /note command"""
    if update.effective_user.id != USER_ID:
        return
    
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("❌ Please provide note text: `/note <text>`", parse_mode='Markdown')
        return
    
    add_note(text)
    await update.message.reply_text(f"✅ Note saved: {text}")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /summary command"""
    if update.effective_user.id != USER_ID:
        return
    
    notes = get_recent_notes(10)
    if not notes:
        await update.message.reply_text("📝 No notes found.")
        return
    
    text = "📊 **Recent Notes:**\n\n"
    for note in notes:
        timestamp = datetime.fromisoformat(note["timestamp"]).strftime("%Y-%m-%d %H:%M")
        text += f"**{timestamp}**\n{note['text']}\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def followup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /followup command"""
    if update.effective_user.id != USER_ID:
        return
    
    notes = get_today_notes()
    if not notes:
        await update.message.reply_text("✅ No follow-ups for today.")
        return
    
    text = "✅ **Today's Follow-ups:**\n\n"
    for note in notes:
        timestamp = datetime.fromisoformat(note["timestamp"]).strftime("%H:%M")
        text += f"**{timestamp}** - {note['text']}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /generate command"""
    if update.effective_user.id != USER_ID:
        return
    
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("❌ Please provide a prompt: `/generate <prompt>`", parse_mode='Markdown')
        return
    
    await update.message.reply_text(f"🤖 Generating with {ai_backend_name}...")
    try:
        result = generate_text(prompt)
        await update.message.reply_text(f"🤖 **Generated Text:**\n\n{result}", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Generation failed: {e}")

async def meeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /meeting command"""
    if update.effective_user.id != USER_ID:
        return
    
    topic = " ".join(context.args) if context.args else "General Discussion"
    link = generate_meeting_link()
    
    await update.message.reply_text(
        f"🔗 **Meeting Link Generated**\n\n"
        f"**Topic:** {topic}\n"
        f"**Link:** {link}",
        parse_mode='Markdown'
    )

async def read_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /readall command"""
    if update.effective_user.id != USER_ID:
        return
    
    await update.message.reply_text("📋 Reading recent messages...")
    
    try:
        async with TelegramClient("session", TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
            messages = []
            async for dialog in client.iter_dialogs(limit=5):
                try:
                    msgs = await client.get_messages(dialog.id, limit=10)
                    for msg in msgs:
                        if msg.message:
                            messages.append(f"[{dialog.name}] {msg.message}")
                except Exception as e:
                    print(f"Error reading messages from {dialog.name}: {e}")
            
            if messages:
                summary = summarize_messages(messages[:50])  # Limit to avoid token limits
                await update.message.reply_text(f"📋 **Message Summary:**\n\n{summary}", parse_mode='Markdown')
            else:
                await update.message.reply_text("📋 No recent messages found.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error reading messages: {e}")

async def brief(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /brief command"""
    if update.effective_user.id != USER_ID:
        return
    
    await update.message.reply_text(f"📅 Generating daily briefing with {ai_backend_name}...")
    
    try:
        # Get today's notes
        notes = get_today_notes()
        
        # Get recent chat summaries
        async def fetch_summary():
            async with TelegramClient("session", TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
                summaries = []
                async for dialog in client.iter_dialogs(limit=3):
                    try:
                        msgs = await client.get_messages(dialog.id, limit=20)
                        texts = [m.message for m in msgs if m.message]
                        if texts:
                            summary = summarize_messages(texts)
                            summaries.append(f"**{dialog.name}:** {summary}")
                    except Exception as e:
                        print(f"Error summarizing {dialog.name}: {e}")
                return summaries
        
        summaries = await fetch_summary()
        brief = generate_brief(notes, summaries)
        
        await update.message.reply_text(f"📅 **Daily Briefing:**\n\n{brief}", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating briefing: {e}")

async def ai_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ai_status command"""
    if update.effective_user.id != USER_ID:
        return
    
    try:
        # Test AI backend
        test_response = ai_chat([{"role": "user", "content": "Say hello in one word."}])
        
        status_text = f"🤖 **AI Backend Status**\n\n"
        status_text += f"**Backend:** {ai_backend_name}\n"
        status_text += f"**Status:** ✅ Active\n"
        status_text += f"**Model:** {ai_client.model if hasattr(ai_client, 'model') else 'Unknown'}\n"
        status_text += f"**Test Response:** {test_response}\n"
        
        if AI_BACKEND == "atoma":
            try:
                network_status = ai_client.get_network_status()
                if "error" not in network_status:
                    status_text += f"**Network Status:** {network_status.get('status', 'Unknown')}\n"
                    status_text += f"**Available Compute:** {network_status.get('available_compute', 'Unknown')}\n"
            except:
                pass
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ AI Status Error: {e}")

async def keyword_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Filter messages for keywords"""
    if update.effective_user.id != USER_ID:
        return
    
    text = update.message.text.lower()
    if any(keyword in text for keyword in KEYWORDS):
        await update.message.reply_text("🔔 **Keyword detected!** This message might need attention.", parse_mode='Markdown')

# === MAIN FUNCTION ===
def main():
    """Main function to run the bot"""
    print(f"🤖 Starting Telegram Manager Bot with {ai_backend_name}...")
    
    # Create application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("note", note))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(CommandHandler("followup", followup))
    application.add_handler(CommandHandler("generate", generate))
    application.add_handler(CommandHandler("meeting", meeting))
    application.add_handler(CommandHandler("readall", read_all))
    application.add_handler(CommandHandler("brief", brief))
    application.add_handler(CommandHandler("leads", sync_sheet))
    application.add_handler(CommandHandler("ai_status", ai_status))
    application.add_handler(CallbackQueryHandler(menu_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_filter))
    
    print("🤖 Bot is running...")
    print(f"🤖 Using AI backend: {ai_backend_name}")
    print("Press Ctrl+C to stop")
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main() 