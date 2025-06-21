#!/usr/bin/env python3
"""
Setup script for Telegram Manager Bot with Unified AI Backend
Supports both Ollama (local) and Atoma (DePIN network)
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

def check_ai_backend():
    """Check which AI backend is configured and test it"""
    print("🔍 Checking AI backend configuration...")
    
    ai_backend = os.getenv("AI_BACKEND", "ollama").lower()
    print(f"📋 Configured AI backend: {ai_backend}")
    
    if ai_backend == "atoma":
        return check_atoma_setup()
    elif ai_backend == "ollama":
        return check_ollama_setup()
    else:
        print(f"❌ Unknown AI backend: {ai_backend}")
        print("   Supported backends: ollama, atoma")
        return False

def check_ollama_setup():
    """Check Ollama installation and setup"""
    print("🔍 Checking Ollama setup...")
    
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
            
            # Check available models
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            if models:
                print(f"✅ Available models: {', '.join(models)}")
            else:
                print("⚠️  No models found. Install a model with: ollama pull llama3.2")
            
            return True
        else:
            print("❌ Ollama server responded with error")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama server not accessible")
        print("   Start Ollama with: ollama serve")
        return False

def check_atoma_setup():
    """Check Atoma API setup"""
    print("🔍 Checking Atoma setup...")
    
    api_key = os.getenv("ATOMA_API_KEY")
    if not api_key or api_key == "your_atoma_api_key_here":
        print("❌ ATOMA_API_KEY not configured")
        print("   Get your API key from: https://atoma.ai")
        return False
    
    print("✅ Atoma API key configured")
    
    # Test Atoma API connection
    try:
        base_url = os.getenv("ATOMA_BASE_URL", "https://api.atoma.ai")
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/v1/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Atoma API connection successful")
            data = response.json()
            models = [model["id"] for model in data.get("data", [])]
            if models:
                print(f"✅ Available models: {', '.join(models)}")
            return True
        else:
            print(f"❌ Atoma API error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Atoma API connection failed: {e}")
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

def suggest_ai_backend():
    """Suggest AI backend based on user preferences"""
    print("\n🤖 AI Backend Options:")
    print("=" * 50)
    print("1. Ollama (Local)")
    print("   ✅ Privacy: All processing on your machine")
    print("   ✅ Cost: Free (no API costs)")
    print("   ✅ Speed: Fast local inference")
    print("   ❌ Setup: Requires local installation")
    print("   ❌ Resources: Uses your computer's resources")
    print()
    print("2. Atoma (DePIN Network)")
    print("   ✅ Setup: No local installation required")
    print("   ✅ Resources: Uses distributed compute")
    print("   ✅ Models: Access to many models")
    print("   ❌ Privacy: Data sent to network")
    print("   ❌ Cost: Pay per use")
    print("   ❌ Dependency: Requires internet connection")
    print()
    print("💡 Recommendation:")
    print("   - For privacy and cost: Use Ollama")
    print("   - For ease of setup: Use Atoma")
    print("   - For production: Consider both (fallback)")

def main():
    """Main setup function"""
    print("🚀 Setting up Telegram Manager Bot with Unified AI Backend")
    print("=" * 70)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Create .env file
    if not create_env_file():
        sys.exit(1)

    # Suggest AI backend options
    suggest_ai_backend()

    # Check AI backend
    if not check_ai_backend():
        print("\n❌ AI backend setup failed")
        print("Please configure either Ollama or Atoma:")
        print("1. For Ollama: Install and start Ollama server")
        print("2. For Atoma: Get API key from https://atoma.ai")
        sys.exit(1)

    print("=" * 70)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your Telegram credentials")
    print("2. Run: python telegram_manager_bot_unified.py")
    print("\n📖 See README_UNIFIED.md for detailed instructions")

if __name__ == "__main__":
    main() 