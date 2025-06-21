#!/usr/bin/env python3
"""
Simple test script to verify the bot is working
"""

import requests
import time

def test_bot_status():
    """Test if the bot is responding"""
    print("🤖 Testing Telegram Bot Status")
    print("=" * 40)
    
    # Get bot token from environment
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ No bot token found in .env file")
        return
    
    # Test bot API
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data["result"]
                print(f"✅ Bot is active!")
                print(f"🤖 Name: {bot_info.get('first_name', 'Unknown')}")
                print(f"👤 Username: @{bot_info.get('username', 'Unknown')}")
                print(f"🆔 Bot ID: {bot_info.get('id', 'Unknown')}")
                print()
                print("📱 **Bot Commands Available:**")
                print("• `/start` - Start the bot")
                print("• `/note <text>` - Save a note")
                print("• `/summary` - View recent notes")
                print("• `/followup` - View today's follow-ups")
                print("• `/generate <prompt>` - Generate text with AI")
                print("• `/meeting` - Generate meeting link")
                print("• `/brief` - Generate daily briefing from notes")
                print("• `/ai_status` - Check AI backend status")
                print()
                print("💡 **Test the bot:**")
                print("1. Open Telegram")
                print("2. Find your bot: @your_bot_username")
                print("3. Send: /start")
                print("4. Try: /note Meeting with client tomorrow")
                print("5. Try: /brief")
                print()
                print("🎉 Bot is ready to use!")
            else:
                print(f"❌ Bot API error: {data.get('description', 'Unknown error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing bot: {e}")

if __name__ == "__main__":
    test_bot_status() 