#!/bin/bash
# Nosana Startup Script
echo "🚀 Starting Telegram Manager Bot on Nosana..."

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH=/app

# Start the bot
python telegram_manager_bot_unified.py
