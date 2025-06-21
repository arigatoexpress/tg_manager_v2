#!/usr/bin/env python3
"""
Setup script for Telegram Manager Bot with Ollama
"""

import os
import sys
import subprocess
import requests

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_ollama_installation():
    """Check if Ollama is installed and running"""
    print("🔍 Checking Ollama installation...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama installed: {result.stdout.strip()}")
        else:
            print("❌ Ollama command failed")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found. Please install Ollama first:")
        print("   Visit: https://ollama.ai/download")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama command timed out")
        return False
    
    # Check if Ollama server is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is running")
            return True
        else:
            print("❌ Ollama server responded with error")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama server not accessible")
        print("   Start Ollama with: ollama serve")
        return False

def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True

    if os.path.exists("env.example"):
        try:
            with open("env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ env.example file not found")
        return False

def suggest_models():
    """Suggest popular Ollama models"""
    print("\n📋 Suggested Ollama models to install:")
    print("   ollama pull llama3.2        # Meta's Llama 3.2 (recommended)")
    print("   ollama pull mistral         # Mistral 7B (fast)")
    print("   ollama pull codellama       # Code-focused model")
    print("   ollama pull phi3            # Microsoft Phi-3 (small & fast)")
    print("\n💡 Install a model with: ollama pull <model_name>")

def main():
    """Main setup function"""
    print("🚀 Setting up Telegram Manager Bot with Ollama...")
    print("=" * 60)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check Ollama installation
    if not check_ollama_installation():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Create .env file
    if not create_env_file():
        sys.exit(1)

    # Suggest models
    suggest_models()

    print("=" * 60)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Install an Ollama model: ollama pull llama3.2")
    print("2. Edit .env file with your Telegram credentials")
    print("3. Run: python telegram_manager_bot_ollama.py")
    print("\n📖 See README.md for detailed instructions")

if __name__ == "__main__":
    main() 