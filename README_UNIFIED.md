# Telegram Manager Bot with Unified AI Backend

A powerful AI-powered Telegram bot that helps you manage your messages, take notes, and get intelligent summaries of your conversations. **Now with support for both local Ollama models and Atoma DePIN network!**

## 🚀 Key Features

- **🤖 Dual AI Backends**: Choose between local Ollama or Atoma DePIN network
- **🔒 Privacy Options**: Local processing with Ollama or distributed compute with Atoma
- **💰 Flexible Cost**: Free local processing or pay-per-use distributed compute
- **⚡ High Performance**: Fast local inference or scalable cloud processing
- **🛠️ Easy Setup**: Simple configuration to switch between backends

## AI Backend Comparison

| Feature | Ollama (Local) | Atoma (DePIN) |
|---------|----------------|---------------|
| **Privacy** | ✅ Full privacy (local) | ❌ Data sent to network |
| **Cost** | ✅ Free | 💰 Pay per use |
| **Setup** | ❌ Requires installation | ✅ No local setup |
| **Resources** | ❌ Uses your computer | ✅ Distributed compute |
| **Speed** | ✅ Fast local inference | ⚡ Network dependent |
| **Models** | ❌ Limited to local models | ✅ Access to many models |
| **Offline** | ✅ Works offline | ❌ Requires internet |

## Prerequisites

### For Ollama (Local AI)
- Python 3.8 or higher
- Ollama installed and running
- At least 8GB RAM (16GB recommended)

### For Atoma (DePIN Network)
- Python 3.8 or higher
- Atoma API key
- Internet connection

### For Both
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/arigatoexpress/telegram_manager_bot.git
cd telegram_manager_bot

# Run the unified setup
python setup_unified.py
```

### 2. Choose Your AI Backend

#### Option A: Ollama (Local AI)

**Install Ollama:**
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

**Start Ollama and Install Model:**
```bash
# Start Ollama server
ollama serve

# In another terminal, install a model
ollama pull llama3.2:latest
```

**Configure Environment:**
```bash
# Edit .env file
AI_BACKEND=ollama
OLLAMA_MODEL=llama3.2:latest
```

#### Option B: Atoma (DePIN Network)

**Get Atoma API Key:**
1. Visit [https://atoma.ai](https://atoma.ai)
2. Sign up for an account
3. Get your API key from the dashboard

**Configure Environment:**
```bash
# Edit .env file
AI_BACKEND=atoma
ATOMA_API_KEY=your_api_key_here
ATOMA_MODEL=llama3.2
```

### 3. Configure Telegram

Edit the `.env` file with your Telegram credentials:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
USER_ID=your_telegram_user_id_here
```

### 4. Test Setup

```bash
# Test everything is working
python test_unified_setup.py
```

### 5. Run the Bot

```bash
# Start the unified bot
python telegram_manager_bot_unified.py
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_BACKEND` | `ollama` | Choose: `ollama` or `atoma` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2:latest` | Ollama model to use |
| `ATOMA_API_KEY` | - | Your Atoma API key |
| `ATOMA_BASE_URL` | `https://api.atoma.ai` | Atoma API URL |
| `ATOMA_MODEL` | `llama3.2` | Atoma model to use |
| `TELEGRAM_BOT_TOKEN` | - | Your Telegram bot token |
| `TELEGRAM_API_ID` | - | Your Telegram API ID |
| `TELEGRAM_API_HASH` | - | Your Telegram API hash |
| `USER_ID` | - | Your Telegram user ID |

### Switching Between Backends

You can easily switch between AI backends by changing the `AI_BACKEND` variable:

```bash
# For local Ollama
AI_BACKEND=ollama

# For Atoma DePIN network
AI_BACKEND=atoma
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
- `/ai_status` - Check AI backend status

## Model Recommendations

### For Ollama (Local)
- **llama3.2:latest** - Best overall performance
- **mistral:latest** - Fast and efficient
- **phi3:latest** - Very fast, good for simple tasks
- **codellama:latest** - Excellent for code-related tasks

### For Atoma (DePIN)
- **llama3.2** - High-quality responses
- **gpt-4** - Best quality (if available)
- **claude-3** - Excellent reasoning
- **mistral** - Fast and cost-effective

## Advanced Usage

### Custom Context

Create a `context.md` file to provide custom instructions to the AI:

```markdown
You are a helpful assistant for a business professional. 
Always be concise and professional in your responses.
Focus on actionable insights and clear recommendations.
```

### Fallback Configuration

You can configure the bot to automatically fallback between backends:

```python
# In telegram_manager_bot_unified.py
def initialize_ai_backend():
    global ai_client, ai_backend_name
    
    # Try Atoma first
    try:
        initialize_atoma_client()
        ai_client = get_atoma_client()
        ai_backend_name = "Atoma DePIN Network"
        return
    except Exception as e:
        print(f"Atoma failed: {e}")
    
    # Fallback to Ollama
    try:
        initialize_ollama_client()
        ai_client = get_ollama_client()
        ai_backend_name = "Local Ollama (Fallback)"
        return
    except Exception as e:
        print(f"Ollama failed: {e}")
    
    raise Exception("No AI backend available")
```

### Usage Monitoring

The bot automatically logs usage statistics for both backends:

```json
{
  "usage": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "backend": "Atoma DePIN Network",
      "prompt_tokens": 100,
      "completion_tokens": 50,
      "total_tokens": 150
    }
  ]
}
```

## Troubleshooting

### Ollama Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Check available models
ollama list

# Install a model
ollama pull llama3.2:latest
```

### Atoma Issues

```bash
# Test Atoma API connection
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.atoma.ai/v1/models

# Check your API key
echo $ATOMA_API_KEY

# Verify network status
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.atoma.ai/v1/network/status
```

### General Issues

1. **Bot not responding**: Check Telegram credentials
2. **AI not working**: Verify AI backend configuration
3. **Slow responses**: Consider switching to a faster model
4. **Memory issues**: Use smaller models or increase system RAM

## Cost Optimization

### For Ollama (Local)
- **Free**: No ongoing costs
- **Hardware**: Consider GPU acceleration for better performance
- **Storage**: Models can take 1-10GB each

### For Atoma (DePIN)
- **Pay per use**: Only pay for what you use
- **Model selection**: Smaller models are cheaper
- **Batch processing**: Group requests to reduce costs
- **Caching**: Implement response caching to avoid repeated requests

## Security Considerations

### Ollama (Local)
- ✅ All data stays on your machine
- ✅ No internet required for AI processing
- ✅ Full control over models and data
- ❌ Requires local resources

### Atoma (DePIN)
- ❌ Data sent to network (encrypted)
- ❌ Requires internet connection
- ✅ No local resource usage
- ✅ Professional-grade security

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify your AI backend configuration
3. Ensure your Telegram credentials are correct
4. Check the bot logs for error messages

For additional help, please open an issue on GitHub.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 