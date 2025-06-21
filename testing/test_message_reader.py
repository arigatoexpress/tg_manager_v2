#!/usr/bin/env python3
"""
Test Telegram Message Reader
============================
Simple test script to verify the message reader setup and functionality.
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        "TELEGRAM_API_ID",
        "TELEGRAM_API_HASH", 
        "TELEGRAM_PHONE"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * len(value)} (hidden)")
    
    if missing_vars:
        print(f"\n❌ Missing or invalid environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print(f"\n💡 Please update your .env file with the correct values.")
        return False
    
    print("✅ All required environment variables are set!")
    return True

async def test_connection():
    """Test basic Telegram connection"""
    print("\n🔌 Testing Telegram connection...")
    
    try:
        from telethon import TelegramClient
        from telethon.errors import SessionPasswordNeededError
        
        api_id_str = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
        phone = os.getenv("TELEGRAM_PHONE")
        
        # Validate environment variables
        if not api_id_str or not api_hash or not phone:
            print("❌ Missing required environment variables")
            return False
        
        api_id = int(api_id_str)
        
        # Create client
        client = TelegramClient("test_session", api_id, api_hash)
        
        # Start client
        await client.start()
        
        if not await client.is_user_authorized():
            print("📱 Please check your phone for the Telegram verification code")
            await client.send_code_request(phone)
            try:
                code = input("Enter the verification code: ")
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                password = input("Enter your 2FA password: ")
                await client.sign_in(password=password)
        
        # Test getting dialogs
        dialog_count = 0
        async for dialog in client.iter_dialogs(limit=5):
            dialog_count += 1
            print(f"   📱 Found chat: {dialog.name} ({dialog.entity.__class__.__name__})")
        
        await client.disconnect()
        
        print(f"✅ Connection successful! Found {dialog_count} chats in preview.")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def show_usage_examples():
    """Show usage examples for the message reader"""
    print("\n📖 MESSAGE READER USAGE EXAMPLES")
    print("=" * 50)
    
    examples = [
        ("Read recent messages from all chats", "python telegram_message_reader.py --recent-days 7"),
        ("Read only user chats (no channels/groups)", "python telegram_message_reader.py --chats-only"),
        ("Search for specific keywords", "python telegram_message_reader.py --keywords urgent important"),
        ("Export to JSON format", "python telegram_message_reader.py --export-format json"),
        ("Generate AI summaries", "python telegram_message_reader.py --summarize"),
        ("Interactive mode", "python telegram_message_reader.py --interactive"),
        ("Limit messages per chat", "python telegram_message_reader.py --limit 100"),
        ("Combine multiple options", "python telegram_message_reader.py --recent-days 30 --chats-only --export-format csv")
    ]
    
    for description, command in examples:
        print(f"\n{description}:")
        print(f"   {command}")

def main():
    """Main test function"""
    print("🧪 TELEGRAM MESSAGE READER TEST")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        print("\n💡 SETUP INSTRUCTIONS:")
        print("1. Get your API credentials from https://my.telegram.org")
        print("2. Add your phone number to the .env file")
        print("3. Run this test again")
        return
    
    # Test connection
    try:
        success = asyncio.run(test_connection())
        if success:
            print("\n🎉 SETUP COMPLETE!")
            show_usage_examples()
            print(f"\n🚀 You can now use the message reader!")
            print(f"   Try: python telegram_message_reader.py --interactive")
        else:
            print("\n❌ Setup incomplete. Please check your credentials.")
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    main() 