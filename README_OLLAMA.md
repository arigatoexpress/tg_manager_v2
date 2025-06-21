# Telegram Manager Bot with Ollama

A powerful AI-powered Telegram bot that helps you manage your messages, take notes, and get intelligent summaries of your conversations using **local Ollama models** instead of cloud APIs.

## 🚀 Key Benefits

- **🔒 Privacy First**: All AI processing happens locally on your machine
- **💰 Cost Effective**: No API costs or usage limits
- **⚡ Fast**: Local inference with no network latency
- **🛠️ Customizable**: Use any Ollama model you prefer
- **🌐 Offline**: Works without internet connection (except for Telegram)

## Features

🤖 **AI-Powered Features**
- Generate professional messages using local Ollama models
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
- Sui smart contract interaction alerts
- Easy meeting link generation
- Custom context for AI prompts
- Sync conversations to Google Sheets for deal tracking

📊 **Daily Briefings**
- AI-generated summaries of your Telegram chats
- Combined insights from notes and conversations
- Actionable follow-up suggestions

## Prerequisites

### 1. Install Ollama

First, install Ollama on your system:

**macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [https://ollama.ai/download](https://ollama.ai/download)

### 2. Start Ollama and Install a Model

```bash
# Start Ollama server
ollama serve

# In another terminal, install a model (choose one):
ollama pull llama3.2        # Meta's Llama 3.2 (recommended)
ollama pull mistral         # Mistral 7B (fast)
ollama pull codellama       # Code-focused model
ollama pull phi3            # Microsoft Phi-3 (small & fast)
```

### 3. Other Requirements

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/arigatoexpress/telegram_manager_bot.git
cd telegram_manager_bot

# Run the Ollama-specific setup
python setup_ollama.py
```

### 2. Configure Environment

Edit the `.env` file with your credentials:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# User Configuration
USER_ID=your_telegram_user_id_here
```

### 3. Test Setup

```bash
# Test everything is working
python test_ollama_setup.py
```

### 4. Run the Bot

```bash
# Start the bot
python telegram_manager_bot_ollama.py
```

## Available Commands

Once the bot is running, you can use these commands in Telegram:

- `/start` - Show the main menu
- `/note <text>` - Save a quick note
- `/summary` - View recent notes
- `/followup` - See today's tasks
- `/generate <prompt>` - Generate AI text
- `/brief` - Get daily briefing
- `/meeting [topic]` - Create meeting link
- `/readall` - Dump recent messages
- `/leads` - Sync to Google Sheets

## Model Recommendations

### For General Use
- **llama3.2** - Best overall performance, good balance of speed and quality
- **mistral** - Fast and efficient, good for quick responses

### For Specific Tasks
- **codellama** - Excellent for code-related tasks
- **phi3** - Very fast, good for simple tasks
- **llama3.1** - Alternative to llama3.2 if you have limited resources

### For Resource-Constrained Systems
- **phi3** - Smallest model, works on most systems
- **mistral:7b** - Good performance with moderate resource usage

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Model to use for AI tasks |
| `TELEGRAM_BOT_TOKEN` | - | Your Telegram bot token |
| `TELEGRAM_API_ID` | - | Your Telegram API ID |
| `TELEGRAM_API_HASH` | - | Your Telegram API hash |
| `USER_ID` | - | Your Telegram user ID |

### Custom Context

Create a `context.md` file to provide custom instructions to the AI:

```markdown
You are a helpful assistant for a business professional. 
Always be concise and professional in your responses.
Focus on actionable insights and clear recommendations.
```

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Check available models
ollama list
```

### Model Not Found

```bash
# Install the model you want to use
ollama pull llama3.2

# Or use a different model by changing OLLAMA_MODEL in .env
```

### Performance Issues

- Use smaller models like `phi3` or `mistral` for faster responses
- Ensure you have enough RAM (at least 8GB recommended)
- Close other resource-intensive applications

### Memory Issues

- Use quantized models (e.g., `llama3.2:3b` instead of `llama3.2`)
- Increase your system's swap space
- Use models with lower parameter counts

## Advanced Usage

### Using Different Models for Different Tasks

You can modify the bot to use different models for different types of tasks by editing the `ollama_client.py` file.

### Custom Model Fine-tuning

Ollama supports custom model fine-tuning. You can create specialized models for your specific use case:

```bash
# Create a custom model
ollama create mybot -f Modelfile

# Use your custom model
export OLLAMA_MODEL=mybot
```

### Integration with Other Services

The bot can be easily extended to integrate with:
- Google Sheets (already included)
- Notion API
- Slack
- Discord
- Email services

## Security Considerations

- All AI processing happens locally on your machine
- No data is sent to external AI services
- Telegram credentials are stored locally in `.env` file
- Consider using environment variables for sensitive data in production

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Ensure Ollama is running and accessible
3. Verify your Telegram credentials are correct
4. Check the bot logs for error messages

For additional help, please open an issue on GitHub. 