#!/usr/bin/env python3
"""
Test script for AI backends (Ollama and Atoma)
Tests the AI functionality without requiring Telegram credentials
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ollama_backend():
    """Test Ollama backend"""
    print("🧪 Testing Ollama Backend...")
    print("=" * 50)
    
    try:
        from ollama_client import initialize_ollama_client, get_ollama_client
        
        # Initialize Ollama
        initialize_ollama_client()
        client = get_ollama_client()
        
        # Test simple chat
        print("📝 Testing simple chat...")
        response = client.chat_completions_create([
            {"role": "user", "content": "Say hello in one word."}
        ])
        
        result = response.choices[0].message["content"]
        print(f"✅ Ollama Response: {result}")
        
        # Test more complex prompt
        print("\n📝 Testing complex prompt...")
        response = client.chat_completions_create([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short professional email to schedule a meeting."}
        ])
        
        result = response.choices[0].message["content"]
        print(f"✅ Ollama Response: {result[:100]}...")
        
        print("\n🎉 Ollama backend test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Ollama backend test FAILED: {e}")
        return False

def test_atoma_backend():
    """Test Atoma backend"""
    print("\n🧪 Testing Atoma Backend...")
    print("=" * 50)
    
    # Check if Atoma API key is configured
    api_key = os.getenv("ATOMA_API_KEY")
    if not api_key or api_key == "your_atoma_api_key_here":
        print("⚠️  Atoma API key not configured")
        print("   To test Atoma:")
        print("   1. Get API key from https://atoma.ai")
        print("   2. Set ATOMA_API_KEY in .env file")
        print("   3. Run this test again")
        return False
    
    try:
        from atoma_client import initialize_atoma_client, get_atoma_client
        
        # Initialize Atoma
        initialize_atoma_client()
        client = get_atoma_client()
        
        # Test simple chat
        print("📝 Testing simple chat...")
        response = client.chat_completions_create([
            {"role": "user", "content": "Say hello in one word."}
        ])
        
        result = response.choices[0].message["content"]
        print(f"✅ Atoma Response: {result}")
        
        # Test more complex prompt
        print("\n📝 Testing complex prompt...")
        response = client.chat_completions_create([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short professional email to schedule a meeting."}
        ])
        
        result = response.choices[0].message["content"]
        print(f"✅ Atoma Response: {result[:100]}...")
        
        print("\n🎉 Atoma backend test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Atoma backend test FAILED: {e}")
        return False

def test_unified_functionality():
    """Test the unified AI chat function"""
    print("\n🧪 Testing Unified AI Functionality...")
    print("=" * 50)
    
    try:
        # Import the unified bot's AI function
        sys.path.append('.')
        from telegram_manager_bot_unified import ai_chat, initialize_ai_backend
        
        # Initialize AI backend (should use Ollama by default)
        initialize_ai_backend()
        
        # Test simple generation
        print("📝 Testing text generation...")
        result = ai_chat([
            {"role": "user", "content": "Generate a professional meeting agenda for a tech startup."}
        ])
        
        print(f"✅ Unified AI Response: {result[:200]}...")
        
        # Test summarization
        print("\n📝 Testing message summarization...")
        messages = [
            "Meeting scheduled for tomorrow at 2pm",
            "Need to prepare presentation slides",
            "Client wants to discuss pricing",
            "Team will join remotely"
        ]
        
        summary = ai_chat([
            {"role": "system", "content": "Summarize these messages and suggest follow-ups."},
            {"role": "user", "content": "\n".join(messages)}
        ])
        
        print(f"✅ Summary: {summary[:200]}...")
        
        print("\n🎉 Unified functionality test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Unified functionality test FAILED: {e}")
        return False

def test_data_storage():
    """Test data storage functionality"""
    print("\n🧪 Testing Data Storage...")
    print("=" * 50)
    
    try:
        from telegram_manager_bot_unified import load_data, save_data, add_note, get_recent_notes
        
        # Test data loading
        data = load_data()
        print("✅ Data loading works")
        
        # Test adding note
        add_note("Test note from AI backend test")
        print("✅ Note addition works")
        
        # Test retrieving notes
        notes = get_recent_notes(5)
        print(f"✅ Retrieved {len(notes)} recent notes")
        
        print("\n🎉 Data storage test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Data storage test FAILED: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Telegram Manager Bot AI Backends")
    print("=" * 70)
    
    tests = [
        ("Ollama Backend", test_ollama_backend),
        ("Atoma Backend", test_atoma_backend),
        ("Unified Functionality", test_unified_functionality),
        ("Data Storage", test_data_storage)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        print()
    
    print("=" * 70)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your AI backends are working correctly.")
        print("\n📋 Next steps:")
        print("1. Configure your Telegram credentials in .env file")
        print("2. Run: python telegram_manager_bot_unified.py")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        if passed >= 2:
            print("💡 At least Ollama is working - you can use the bot with local AI!")
    
    return passed == total

if __name__ == "__main__":
    main() 