#!/usr/bin/env python3
"""
Interactive setup script for Telegram bot environment variables
"""

import os
import sys

def setup_telegram_env():
    """Interactive setup for Telegram environment variables"""
    print("🤖 Telegram Bot Environment Setup")
    print("=" * 50)
    print()
    print("This script will help you set up the environment variables needed for the Telegram bot.")
    print("You can skip any values you don't have yet by pressing Enter.")
    print()
    
    env_vars = {}
    
    # Telegram Bot Configuration
    print("📱 Telegram Bot Configuration:")
    print("-" * 30)
    env_vars["TELEGRAM_BOT_TOKEN"] = input("Bot Token (from @BotFather): ").strip() or "your_bot_token_here"
    env_vars["TELEGRAM_API_ID"] = input("API ID (from https://my.telegram.org): ").strip() or "your_api_id_here"
    env_vars["TELEGRAM_API_HASH"] = input("API Hash (from https://my.telegram.org): ").strip() or "your_api_hash_here"
    env_vars["USER_ID"] = input("Your Telegram User ID: ").strip() or "your_telegram_user_id_here"
    
    print()
    print("🤖 AI Backend Configuration:")
    print("-" * 30)
    ai_backend = input("AI Backend (ollama/atoma) [ollama]: ").strip() or "ollama"
    env_vars["AI_BACKEND"] = ai_backend
    
    if ai_backend == "ollama":
        env_vars["OLLAMA_BASE_URL"] = input("Ollama URL [http://localhost:11434]: ").strip() or "http://localhost:11434"
        env_vars["OLLAMA_MODEL"] = input("Ollama Model [llama3.2:latest]: ").strip() or "llama3.2:latest"
    elif ai_backend == "atoma":
        env_vars["ATOMA_API_KEY"] = input("Atoma API Key: ").strip() or "your_atoma_api_key_here"
        env_vars["ATOMA_BASE_URL"] = input("Atoma URL [https://api.atoma.ai]: ").strip() or "https://api.atoma.ai"
        env_vars["ATOMA_MODEL"] = input("Atoma Model [llama3.2]: ").strip() or "llama3.2"
    
    print()
    print("📋 Other Configuration:")
    print("-" * 30)
    env_vars["CONTEXT_FILE"] = input("Context File [context.md]: ").strip() or "context.md"
    env_vars["MEETING_URL_BASE"] = input("Meeting URL Base [https://meet.jit.si]: ").strip() or "https://meet.jit.si"
    
    # Write to .env file
    env_content = "# Telegram Bot Configuration\n"
    env_content += f"TELEGRAM_BOT_TOKEN={env_vars['TELEGRAM_BOT_TOKEN']}\n"
    env_content += f"TELEGRAM_API_ID={env_vars['TELEGRAM_API_ID']}\n"
    env_content += f"TELEGRAM_API_HASH={env_vars['TELEGRAM_API_HASH']}\n"
    env_content += f"USER_ID={env_vars['USER_ID']}\n\n"
    
    env_content += "# AI Backend Configuration\n"
    env_content += f"AI_BACKEND={env_vars['AI_BACKEND']}\n\n"
    
    if ai_backend == "ollama":
        env_content += "# Ollama Configuration\n"
        env_content += f"OLLAMA_BASE_URL={env_vars['OLLAMA_BASE_URL']}\n"
        env_content += f"OLLAMA_MODEL={env_vars['OLLAMA_MODEL']}\n\n"
    elif ai_backend == "atoma":
        env_content += "# Atoma Configuration\n"
        env_content += f"ATOMA_API_KEY={env_vars['ATOMA_API_KEY']}\n"
        env_content += f"ATOMA_BASE_URL={env_vars['ATOMA_BASE_URL']}\n"
        env_content += f"ATOMA_MODEL={env_vars['ATOMA_MODEL']}\n\n"
    
    env_content += "# Other Configuration\n"
    env_content += f"CONTEXT_FILE={env_vars['CONTEXT_FILE']}\n"
    env_content += f"MEETING_URL_BASE={env_vars['MEETING_URL_BASE']}\n"
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print()
        print("✅ Environment file created successfully!")
        print("📁 File: .env")
        print()
        print("📋 Next steps:")
        print("1. Edit .env file with your actual credentials")
        print("2. Run: python telegram_manager_bot_unified.py")
        print()
        print("💡 To get Telegram credentials:")
        print("   • Bot Token: Message @BotFather on Telegram")
        print("   • API ID/Hash: Visit https://my.telegram.org")
        print("   • User ID: Use @userinfobot on Telegram")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        print("Please create the file manually using env.example as a template")

if __name__ == "__main__":
    setup_telegram_env() 