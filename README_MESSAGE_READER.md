# Telegram Message Reader

A comprehensive tool to read and process all your Telegram messages using the user-level API (Telethon).

## 🚀 Features

- **Full Message Access**: Read all messages from all your Telegram chats, groups, and channels
- **Smart Filtering**: Filter by date range, chat type, or keywords
- **Multiple Export Formats**: Export to JSON, CSV, or readable text
- **AI-Powered Analysis**: Generate summaries and insights using local Ollama or Atoma DePIN
- **Interactive Mode**: Browse and search messages interactively
- **Privacy-Focused**: All processing happens locally on your machine
- **Performance Optimized**: Efficient message processing with progress indicators

## 📋 Prerequisites

1. **Telegram API Credentials**: Get from https://my.telegram.org
   - API ID
   - API Hash
   - Phone number

2. **Python Environment**: Same as the main bot setup

3. **AI Backend** (Optional): For summarization features
   - Ollama (local) or Atoma (DePIN network)

## 🔧 Setup

### 1. Environment Configuration

Your `.env` file should include:

```env
# Telegram API Credentials
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=your_phone_number_here

# AI Backend (Optional)
AI_BACKEND=ollama  # or "atoma"
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

### 2. Add Your Phone Number

Run the setup script to add your phone number:

```bash
python setup_phone.py
```

Or manually add to your `.env` file:
```env
TELEGRAM_PHONE=+1234567890
```

### 3. Test Setup

Verify everything is working:

```bash
python test_message_reader.py
```

## 📖 Usage

### Basic Commands

```bash
# Interactive mode (recommended for first use)
python telegram_message_reader.py --interactive

# Read recent messages (last 7 days)
python telegram_message_reader.py --recent-days 7

# Read only user chats (no channels/groups)
python telegram_message_reader.py --chats-only

# Search for specific keywords
python telegram_message_reader.py --keywords urgent important

# Export to JSON format
python telegram_message_reader.py --export-format json

# Generate AI summaries
python telegram_message_reader.py --summarize

# Limit messages per chat
python telegram_message_reader.py --limit 100
```

### Advanced Usage

```bash
# Combine multiple options
python telegram_message_reader.py --recent-days 30 --chats-only --export-format csv --summarize

# Read specific date range with keyword filtering
python telegram_message_reader.py --recent-days 14 --keywords meeting deadline

# Export with AI analysis
python telegram_message_reader.py --export-format json --summarize
```

## 🎯 Interactive Mode

The interactive mode provides a user-friendly interface:

```
🎯 INTERACTIVE MODE
==============================

Options:
1. Search messages by keyword
2. View messages from specific chat
3. Generate AI summary
4. Export messages
5. Show statistics
6. Exit
```

### Interactive Features

- **Keyword Search**: Find messages containing specific words
- **Chat Browser**: Browse messages from specific conversations
- **AI Summaries**: Generate intelligent summaries of conversations
- **Export Options**: Save data in various formats
- **Statistics**: View message counts and date ranges

## 📊 Export Formats

### JSON Format
```json
{
  "export_date": "2024-01-15T10:30:00",
  "total_messages": 1250,
  "chats": {...},
  "messages": [
    {
      "id": 123,
      "date": "2024-01-15T10:00:00",
      "chat_title": "John Doe",
      "sender_name": "John Doe",
      "text": "Hello there!",
      "is_outgoing": false
    }
  ]
}
```

### CSV Format
- Comma-separated values with headers
- Easy to import into Excel, Google Sheets, or databases
- Includes all message metadata

### Text Format
- Human-readable format
- Organized by chat
- Shows message flow with timestamps

## 🤖 AI Features

### Summarization
Generate intelligent summaries of conversations:

```bash
python telegram_message_reader.py --summarize
```

### AI Backend Options

1. **Ollama (Local)**: 
   - Fast, private, no internet required
   - Uses your local AI model
   - Recommended for privacy

2. **Atoma (DePIN Network)**:
   - Distributed computing network
   - Pay-per-use model
   - Good for complex analysis

## 🔒 Privacy & Security

- **Local Processing**: All data stays on your machine
- **No Cloud Storage**: Messages are never uploaded to external servers
- **Session Management**: Secure authentication with Telegram
- **Optional AI**: AI features are completely optional

## 📈 Performance Tips

1. **Use Date Filters**: Limit to recent messages for faster processing
2. **Chat Filtering**: Use `--chats-only` to skip large groups/channels
3. **Message Limits**: Use `--limit` to cap messages per chat
4. **Keyword Filtering**: Filter early to reduce processing time

## 🛠️ Troubleshooting

### Common Issues

1. **"Missing environment variables"**
   - Run `python setup_phone.py` to add phone number
   - Check your `.env` file has all required variables

2. **"Connection failed"**
   - Verify API credentials from https://my.telegram.org
   - Check internet connection
   - Ensure phone number is in international format

3. **"Session password needed"**
   - Enter your 2FA password when prompted
   - This is normal for accounts with two-factor authentication

4. **"No AI backend available"**
   - Start Ollama: `ollama serve`
   - Or configure Atoma API key
   - AI features are optional

### Getting Help

1. Run the test script: `python test_message_reader.py`
2. Check the logs for specific error messages
3. Verify your Telegram API credentials
4. Ensure your phone number is correct

## 🔗 Integration with Bot

The main Telegram bot now includes information about the message reader:

- Use `/readall` in the bot to get setup instructions
- The bot and message reader work independently
- Bot for real-time interactions, reader for historical analysis

## 📝 Examples

### Daily Message Review
```bash
# Get yesterday's messages
python telegram_message_reader.py --recent-days 1 --export-format txt

# Search for urgent items
python telegram_message_reader.py --recent-days 7 --keywords urgent asap important
```

### Meeting Preparation
```bash
# Get recent meeting-related messages
python telegram_message_reader.py --keywords meeting agenda schedule

# Generate summary of project discussions
python telegram_message_reader.py --keywords project deadline --summarize
```

### Data Export
```bash
# Export all messages for backup
python telegram_message_reader.py --export-format json

# Export recent work conversations
python telegram_message_reader.py --recent-days 30 --chats-only --export-format csv
```

## 🎉 Getting Started

1. **Setup**: `python setup_phone.py`
2. **Test**: `python test_message_reader.py`
3. **Explore**: `python telegram_message_reader.py --interactive`
4. **Export**: `python telegram_message_reader.py --export-format json`

Enjoy reading and analyzing your Telegram messages! 🚀 