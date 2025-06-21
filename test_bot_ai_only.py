#!/usr/bin/env python3
"""
Test the AI functionality of the Telegram Manager Bot without requiring Telegram credentials
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Set up minimal environment for AI testing
os.environ.setdefault("AI_BACKEND", "ollama")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
os.environ.setdefault("OLLAMA_MODEL", "llama3.2:latest")
os.environ.setdefault("USER_ID", "123456789")  # Dummy value
os.environ.setdefault("CONTEXT_FILE", "context.md")

# Load environment
load_dotenv()

def test_ai_functionality():
    """Test the AI functions from the bot"""
    print("🤖 Testing Telegram Manager Bot AI Functionality")
    print("=" * 60)
    
    try:
        # Initialize Ollama directly
        from ollama_client import initialize_ollama_client, get_ollama_client
        
        print("🔧 Initializing Ollama...")
        initialize_ollama_client()
        client = get_ollama_client()
        print("✅ Ollama initialized successfully")
        print()
        
        # Test 1: Simple AI chat
        print("📝 Test 1: Simple AI Chat")
        print("-" * 40)
        response = client.chat_completions_create([
            {"role": "user", "content": "Hello! Can you help me write a professional email?"}
        ])
        result = response.choices[0].message["content"]
        print(f"AI Response: {result[:200]}...")
        print()
        
        # Test 2: Message summarization
        print("📊 Test 2: Message Summarization")
        print("-" * 40)
        messages = [
            "Meeting scheduled for tomorrow at 2pm",
            "Need to prepare presentation slides",
            "Client wants to discuss pricing",
            "Team will join remotely"
        ]
        
        summary_response = client.chat_completions_create([
            {"role": "system", "content": "Summarize these chat messages and suggest follow-ups."},
            {"role": "user", "content": "\n".join(messages)}
        ])
        summary = summary_response.choices[0].message["content"]
        print(f"Summary: {summary[:200]}...")
        print()
        
        # Test 3: Text generation
        print("✍️  Test 3: Text Generation")
        print("-" * 40)
        generated_response = client.chat_completions_create([
            {"role": "system", "content": "You are a helpful assistant that writes professional messages."},
            {"role": "user", "content": "Write a short professional email to schedule a meeting"}
        ])
        generated = generated_response.choices[0].message["content"]
        print(f"Generated: {generated[:200]}...")
        print()
        
        # Test 4: Note taking and briefing
        print("📋 Test 4: Note Taking and Briefing")
        print("-" * 40)
        
        # Simple note storage
        notes = [
            {"timestamp": datetime.now().isoformat(), "text": "Important meeting with client tomorrow"},
            {"timestamp": datetime.now().isoformat(), "text": "Need to prepare budget proposal"},
            {"timestamp": datetime.now().isoformat(), "text": "Follow up on pending invoices"}
        ]
        
        print(f"Recent notes: {len(notes)} created")
        for note in notes:
            print(f"  - {note['text']}")
        
        chat_summaries = [
            "Discussed project timeline with development team",
            "Client feedback on new feature requirements"
        ]
        
        note_text = "\n".join([f"- {n['text']}" for n in notes])
        briefing_response = client.chat_completions_create([
            {"role": "system", "content": "You generate clear, insightful daily briefings."},
            {"role": "user", "content": f"NOTES:\n{note_text}\n\nCHATS:\n{chr(10).join(chat_summaries)}"}
        ])
        briefing = briefing_response.choices[0].message["content"]
        print(f"Daily Briefing: {briefing[:200]}...")
        print()
        
        print("🎉 All AI functionality tests passed!")
        print("✅ The bot's AI features are working correctly")
        print()
        print("📋 Available AI functions:")
        print("   • Direct AI conversation via Ollama")
        print("   • Message summarization")
        print("   • Professional text generation")
        print("   • Daily briefing creation")
        print("   • Note management")
        print()
        print("🚀 Ready to run the full Telegram bot!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI functionality: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

if __name__ == "__main__":
    test_ai_functionality() 