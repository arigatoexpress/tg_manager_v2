#!/usr/bin/env python3
"""
Test script for Telegram Manager Bot with Ollama setup
"""

import os
import sys
import importlib
import requests

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")

    required_packages = [
        "telethon",
        "telegram",
        "dotenv",
        "schedule",
        "asyncio",
        "requests"
    ]

    failed_imports = []

    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            failed_imports.append(package)

    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("✅ All imports successful")
    return True

def test_ollama_connection():
    """Test Ollama connection and model availability"""
    print("\n🔍 Testing Ollama connection...")
    
    try:
        # Test basic connection
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama server not responding")
            return False
        
        print("✅ Ollama server is running")
        
        # Test model availability
        data = response.json()
        models = [model["name"] for model in data.get("models", [])]
        
        if not models:
            print("⚠️  No models found. Install a model with: ollama pull llama3.2")
            return True  # Don't fail the test, just warn
        
        print(f"✅ Found models: {', '.join(models)}")
        
        # Test if the configured model is available
        configured_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        if configured_model in models:
            print(f"✅ Configured model '{configured_model}' is available")
        else:
            print(f"⚠️  Configured model '{configured_model}' not found")
            print(f"   Available models: {', '.join(models)}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ollama connection failed: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return False

def test_env_file():
    """Test if .env file exists and has required variables"""
    print("\n🔍 Testing environment configuration...")

    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("Run: python setup_ollama.py")
        return False

    print("✅ .env file exists")

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_API_ID",
        "TELEGRAM_API_HASH",
        "USER_ID"
    ]

    optional_vars = [
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL"
    ]

    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            print(f"❌ {var} not configured")
            missing_vars.append(var)
        else:
            print(f"✅ {var} configured")

    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} configured: {value}")
        else:
            print(f"⚠️  {var} using default value")

    if missing_vars:
        print(f"\n❌ Missing or invalid variables: {', '.join(missing_vars)}")
        print("Please edit .env file with your actual credentials")
        return False

    print("✅ All environment variables configured")
    return True

def test_ollama_client():
    """Test the Ollama client functionality"""
    print("\n🔍 Testing Ollama client...")
    
    try:
        from ollama_client import initialize_ollama_client, get_ollama_client
        
        # Initialize client
        initialize_ollama_client()
        
        # Test basic functionality
        client = get_ollama_client()
        
        # Test a simple prompt
        response = client.chat_completions_create([
            {"role": "user", "content": "Say hello in one word."}
        ])
        
        if response.choices and response.choices[0].message["content"]:
            print("✅ Ollama client working correctly")
            return True
        else:
            print("❌ Ollama client returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Ollama client test failed: {e}")
        return False

def test_data_file():
    """Test if data file can be created"""
    print("\n🔍 Testing data storage...")

    try:
        import json
        from datetime import datetime

        test_data = {
            "notes": [{"timestamp": datetime.now().isoformat(), "text": "test"}],
            "usage": []
        }

        with open("test_data.json", "w") as f:
            json.dump(test_data, f, indent=2)

        with open("test_data.json", "r") as f:
            loaded_data = json.load(f)

        os.remove("test_data.json")

        if loaded_data["notes"][0]["text"] == "test":
            print("✅ Data storage working")
            return True
        else:
            print("❌ Data storage test failed")
            return False

    except Exception as e:
        print(f"❌ Data storage test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Telegram Manager Bot with Ollama Setup")
    print("=" * 60)

    tests = [
        test_imports,
        test_ollama_connection,
        test_env_file,
        test_ollama_client,
        test_data_file
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("Run: python telegram_manager_bot_ollama.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 