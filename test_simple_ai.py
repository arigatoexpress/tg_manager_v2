#!/usr/bin/env python3
"""
Simple test for AI backends without importing the full bot
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ollama_direct():
    """Test Ollama directly"""
    print("🧪 Testing Ollama Directly...")
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
        
        print("\n🎉 Ollama test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Ollama test FAILED: {e}")
        return False

def test_atoma_direct():
    """Test Atoma directly"""
    print("\n🧪 Testing Atoma Directly...")
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
        
        print("\n🎉 Atoma test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Atoma test FAILED: {e}")
        return False

def test_data_storage_simple():
    """Test data storage without importing the full bot"""
    print("\n🧪 Testing Data Storage...")
    print("=" * 50)
    
    try:
        import json
        from datetime import datetime
        
        # Test data file operations
        test_data = {
            "notes": [{"timestamp": datetime.now().isoformat(), "text": "test note"}],
            "usage": []
        }
        
        # Write test data
        with open("test_data.json", "w") as f:
            json.dump(test_data, f, indent=2)
        print("✅ Data writing works")
        
        # Read test data
        with open("test_data.json", "r") as f:
            loaded_data = json.load(f)
        print("✅ Data reading works")
        
        # Clean up
        os.remove("test_data.json")
        print("✅ Data cleanup works")
        
        print("\n🎉 Data storage test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Data storage test FAILED: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Simple AI Backend Tests")
    print("=" * 50)
    
    # Wait a moment for Ollama to start
    print("⏳ Waiting for Ollama to start...")
    time.sleep(3)
    
    tests = [
        ("Ollama", test_ollama_direct),
        ("Atoma", test_atoma_direct),
        ("Data Storage", test_data_storage_simple)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed >= 2:
        print("🎉 Core functionality is working!")
        print("\n📋 Next steps:")
        print("1. Configure your Telegram credentials in .env file")
        print("2. Run: python telegram_manager_bot_unified.py")
    else:
        print("❌ Some core tests failed. Please check the issues above.")
    
    return passed >= 2

if __name__ == "__main__":
    main() 