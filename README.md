# Telegram Manager Bot

A powerful AI-powered Telegram bot that helps you manage your messages, take notes, and get intelligent summaries of your conversations.

## Features

🤖 **AI-Powered Features**
- Generate professional messages using OpenAI GPT-4
- Intelligent summarization of chat conversations
- Daily briefings combining notes and chat summaries

📝 **Note Management**
- Save quick notes with timestamps
- View recent notes and today's notes
- Search and filter notes by keywords

🔔 **Smart Monitoring**
- Keyword detection for important messages
- Automatic alerts for urgent content
- Follow-up tracking for tasks and action items

📊 **Daily Briefings**
- AI-generated summaries of your Telegram chats
- Combined insights from notes and conversations
- Actionable follow-up suggestions

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))
- OpenAI API key (from [OpenAI Platform](https://platform.openai.com))

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/arigatoexpress/telegram_manager_bot.git
cd telegram_manager_bot

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` with your credentials:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# User Configuration
USER_ID=your_telegram_user_id_here
```

### 4. Getting Your Credentials

**Telegram Bot Token:**
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token provided

**Telegram API Credentials:**
1. Visit [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Copy the `api_id` and `api_hash`

**OpenAI API Key:**
1. Visit [OpenAI Platform](https://platform.openai.com)
2. Create an account or log in
3. Go to API Keys section
4. Create a new API key

**Your Telegram User ID:**
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your user ID

### 5. Running the Bot

```bash
python telegram_manager_bot.py
```

## Usage

### Commands

- `/start` - Show the main menu with interactive buttons
- `/note <text>` - Save a note
- `/summary` - View recent notes
- `/followup` - Show today's follow-up tasks
- `/generate <prompt>` - Generate AI-powered text
- `/brief` - Get a comprehensive daily briefing

### Interactive Menu

The bot provides an intuitive menu with buttons for:
- 📋 **Brief** - Get daily AI-powered briefing
- 📝 **Note** - Quick note-taking
- 📊 **Summary** - View your notes
- 📅 **Follow-up** - Track action items
- 🧠 **Generate** - AI text generation
- ℹ️ **Help** - Show available commands

### Keyword Monitoring

The bot automatically monitors messages for important keywords:
- urgent, invoice, asap, important, reminder
- deadline, follow up, todo, meeting
- action required, payment, feedback
- review, blocker, question, help, fix, resolve

## Data Storage

The bot stores data locally in `data_store.json`:
- Notes with timestamps
- OpenAI API usage statistics
- Chat summaries and briefings

## Customization

### Adding Keywords

Edit the `KEYWORDS` list in `telegram_manager_bot.py`:

```python
KEYWORDS = [
    "urgent", "invoice", "@yourname", "asap", "important", "reminder",
    "deadline", "follow up", "todo", "meeting", "action required", "payment",
    "feedback", "review", "blocker", "question", "help", "fix", "resolve",
    "your_custom_keyword"  # Add your own keywords here
]
```

### Modifying AI Prompts

You can customize the AI behavior by editing the system prompts in the functions:
- `summarize_messages()` - Chat summarization
- `generate_text()` - Text generation
- `generate_brief()` - Daily briefing

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure
- The bot only responds to the user ID specified in the configuration
- All data is stored locally on your machine

## Troubleshooting

**Bot not responding:**
- Check that your `USER_ID` is correct
- Verify your bot token is valid
- Ensure the bot is running without errors

**Telethon connection issues:**
- Verify your `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`
- Make sure you're using the correct phone number
- Check your internet connection

**OpenAI API errors:**
- Verify your OpenAI API key is valid
- Check your OpenAI account has sufficient credits
- Ensure you're using a supported model

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.