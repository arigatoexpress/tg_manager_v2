#!/usr/bin/env python3
"""
Telegram Message Reader
=======================
A comprehensive tool to read and process all Telegram messages using the user-level API.

Features:
- Read all messages from all chats
- Filter by date range, chat type, or keywords
- Export to various formats (JSON, CSV, TXT)
- AI-powered summarization and analysis
- Search and filtering capabilities
- Privacy-focused with local processing

Usage:
    python telegram_message_reader.py [options]
    
Options:
    --chats-only     Read only chat messages (no channels/groups)
    --recent-days N  Read messages from last N days
    --export-format  Export format (json, csv, txt)
    --keywords       Filter by keywords
    --summarize      Generate AI summaries
    --interactive    Interactive mode
"""

import os
import sys
import json
import csv
import asyncio
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel, Message
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv

# Import our AI clients for summarization
from ollama_client import initialize_ollama_client, get_ollama_client
from atoma_client import initialize_atoma_client, get_atoma_client

# Load environment variables
load_dotenv()

@dataclass
class MessageData:
    """Data structure for message information"""
    id: int
    date: str
    chat_id: int
    chat_title: str
    chat_type: str
    sender_id: Optional[int]
    sender_name: str
    text: str
    is_outgoing: bool
    reply_to: Optional[int]
    forwarded_from: Optional[str]
    media_type: Optional[str]
    file_size: Optional[int]

class TelegramMessageReader:
    """Main class for reading Telegram messages"""
    
    def __init__(self):
        self.client = None
        self.ai_client = None
        self.messages = []
        self.chats = {}
        
        # Load credentials
        self.api_id = int(os.getenv("TELEGRAM_API_ID"))
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        
        if not all([self.api_id, self.api_hash, self.phone]):
            raise ValueError("Missing Telegram credentials in .env file")
        
        # Initialize AI backend
        self._initialize_ai()
    
    def _initialize_ai(self):
        """Initialize AI backend for summarization"""
        try:
            ai_backend = os.getenv("AI_BACKEND", "ollama").lower()
            
            if ai_backend == "atoma":
                initialize_atoma_client()
                self.ai_client = get_atoma_client()
                print("✅ Atoma DePIN network initialized for summarization")
            else:
                initialize_ollama_client()
                self.ai_client = get_ollama_client()
                print("✅ Ollama initialized for summarization")
                
        except Exception as e:
            print(f"⚠️  AI backend not available: {e}")
            self.ai_client = None
    
    async def connect(self):
        """Connect to Telegram"""
        print("🔌 Connecting to Telegram...")
        
        # Create client
        session_name = "telegram_reader_session"
        self.client = TelegramClient(session_name, self.api_id, self.api_hash)
        
        # Start client
        await self.client.start(phone=self.phone)
        
        if not await self.client.is_user_authorized():
            print("📱 Please check your phone for the Telegram verification code")
            await self.client.send_code_request(self.phone)
            try:
                await self.client.sign_in(self.phone, input("Enter the code: "))
            except SessionPasswordNeededError:
                await self.client.sign_in(password=input("Enter your 2FA password: "))
        
        print("✅ Connected to Telegram")
    
    async def get_chats(self, chats_only: bool = False) -> Dict[int, Any]:
        """Get all chats/dialogs"""
        print("📋 Fetching chats...")
        
        async for dialog in self.client.iter_dialogs():
            chat = dialog.entity
            
            # Filter by chat type if requested
            if chats_only and not isinstance(chat, User):
                continue
            
            chat_info = {
                'id': chat.id,
                'title': getattr(chat, 'title', None) or getattr(chat, 'first_name', 'Unknown'),
                'type': self._get_chat_type(chat),
                'username': getattr(chat, 'username', None),
                'is_verified': getattr(chat, 'verified', False),
                'is_scam': getattr(chat, 'scam', False),
                'is_fake': getattr(chat, 'fake', False),
                'participants_count': getattr(chat, 'participants_count', None)
            }
            
            self.chats[chat.id] = chat_info
        
        print(f"✅ Found {len(self.chats)} chats")
        return self.chats
    
    def _get_chat_type(self, chat) -> str:
        """Determine chat type"""
        if isinstance(chat, User):
            return "user"
        elif isinstance(chat, Chat):
            return "group"
        elif isinstance(chat, Channel):
            return "channel" if chat.broadcast else "supergroup"
        return "unknown"
    
    async def read_messages(self, 
                          chat_ids: Optional[List[int]] = None,
                          limit: Optional[int] = None,
                          recent_days: Optional[int] = None,
                          keywords: Optional[List[str]] = None) -> List[MessageData]:
        """Read messages from specified chats"""
        print("📖 Reading messages...")
        
        # Determine date filter
        date_filter = None
        if recent_days:
            date_filter = datetime.now() - timedelta(days=recent_days)
        
        # Get chats to process
        if chat_ids is None:
            chat_ids = list(self.chats.keys())
        
        total_messages = 0
        filtered_messages = 0
        
        for chat_id in chat_ids:
            if chat_id not in self.chats:
                continue
            
            chat_info = self.chats[chat_id]
            print(f"📱 Reading from: {chat_info['title']} ({chat_info['type']})")
            
            try:
                # Get messages
                messages = self.client.iter_messages(
                    chat_id,
                    limit=limit,
                    offset_date=date_filter
                )
                
                async for message in messages:
                    total_messages += 1
                    
                    # Skip non-text messages for now
                    if not message.text:
                        continue
                    
                    # Apply keyword filter
                    if keywords and not any(kw.lower() in message.text.lower() for kw in keywords):
                        continue
                    
                    # Get sender info
                    sender_name = "Unknown"
                    if message.sender_id:
                        try:
                            sender = await self.client.get_entity(message.sender_id)
                            if hasattr(sender, 'first_name'):
                                sender_name = f"{getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}".strip()
                            elif hasattr(sender, 'title'):
                                sender_name = sender.title
                        except:
                            sender_name = f"User {message.sender_id}"
                    
                    # Create message data
                    msg_data = MessageData(
                        id=message.id,
                        date=message.date.isoformat(),
                        chat_id=chat_id,
                        chat_title=chat_info['title'],
                        chat_type=chat_info['type'],
                        sender_id=message.sender_id,
                        sender_name=sender_name,
                        text=message.text,
                        is_outgoing=message.out,
                        reply_to=message.reply_to_msg_id,
                        forwarded_from=getattr(message.forward, 'from_id', None),
                        media_type=message.media.__class__.__name__ if message.media else None,
                        file_size=getattr(message.media, 'size', None) if message.media else None
                    )
                    
                    self.messages.append(msg_data)
                    filtered_messages += 1
                    
                    # Progress indicator
                    if total_messages % 100 == 0:
                        print(f"   📊 Processed {total_messages} messages, filtered: {filtered_messages}")
                
            except Exception as e:
                print(f"❌ Error reading from {chat_info['title']}: {e}")
        
        print(f"✅ Read {total_messages} total messages, filtered: {filtered_messages}")
        return self.messages
    
    async def generate_summaries(self) -> Dict[str, str]:
        """Generate AI summaries for chats with executive, conversion-optimized focus"""
        if not self.ai_client:
            print("⚠️  No AI backend available for summarization")
            return {}
        
        print("🤖 Generating executive business briefs and conversion-optimized recommendations...")
        summaries = {}
        
        # Group messages by chat
        chat_messages = {}
        for msg in self.messages:
            if msg.chat_id not in chat_messages:
                chat_messages[msg.chat_id] = []
            chat_messages[msg.chat_id].append(msg)
        
        for chat_id, messages in chat_messages.items():
            chat_title = self.chats[chat_id]['title']
            print(f"   📝 Summarizing {chat_title} ({len(messages)} messages)")
            
            try:
                # Prepare text for summarization
                text_samples = []
                for msg in messages[-50:]:  # Use last 50 messages for context
                    text_samples.append(f"[{msg.sender_name}]: {msg.text}")
                
                if not text_samples:
                    continue
                
                text_block = "\n".join(text_samples)
                
                # Executive, conversion-optimized prompt
                prompt = f"""
You are a senior business development executive. Analyze the following recent conversation from the chat '{chat_title}'.

Your response must be:
- Professional, stoic, and concise
- Structured for executive review
- Focused on conversion, actionable next steps, and business growth

**Format your output as follows:**

Executive Brief:
- [2-3 sentence summary of the business context and tone]

Key Insights:
- [Bullet points of the most important facts, opportunities, and risks]

Conversion Opportunities:
- [List specific actions or messages that could drive a deal, partnership, or client commitment]

Actionable Recommendations:
- [Clear, prioritized next steps for the team to maximize conversion and business value]

Next Steps:
- [Succinct, authoritative instructions for immediate follow-up]

Conversation:
{text_block}
"""
                
                response = self.ai_client.chat_completions_create(
                    messages=[
                        {"role": "system", "content": "You are a senior business development executive. Your tone is professional, stoic, and focused on conversion and business growth."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                
                summary = response.choices[0].message["content"]
                summaries[chat_title] = summary
                
            except Exception as e:
                print(f"❌ Error summarizing {chat_title}: {e}")
        
        return summaries
    
    def export_json(self, filename: str = "telegram_messages.json"):
        """Export messages to JSON"""
        print(f"💾 Exporting to {filename}...")
        
        data = {
            'export_date': datetime.now().isoformat(),
            'total_messages': len(self.messages),
            'chats': self.chats,
            'messages': [asdict(msg) for msg in self.messages]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(self.messages)} messages to {filename}")
    
    def export_csv(self, filename: str = "telegram_messages.csv"):
        """Export messages to CSV"""
        print(f"💾 Exporting to {filename}...")
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'ID', 'Date', 'Chat ID', 'Chat Title', 'Chat Type',
                'Sender ID', 'Sender Name', 'Text', 'Is Outgoing',
                'Reply To', 'Forwarded From', 'Media Type', 'File Size'
            ])
            
            # Write messages
            for msg in self.messages:
                writer.writerow([
                    msg.id, msg.date, msg.chat_id, msg.chat_title, msg.chat_type,
                    msg.sender_id, msg.sender_name, msg.text, msg.is_outgoing,
                    msg.reply_to, msg.forwarded_from, msg.media_type, msg.file_size
                ])
        
        print(f"✅ Exported {len(self.messages)} messages to {filename}")
    
    def export_txt(self, filename: str = "telegram_messages.txt"):
        """Export messages to readable text format"""
        print(f"💾 Exporting to {filename}...")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Telegram Messages Export\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Messages: {len(self.messages)}\n")
            f.write("=" * 80 + "\n\n")
            
            # Group by chat
            chat_messages = {}
            for msg in self.messages:
                if msg.chat_id not in chat_messages:
                    chat_messages[msg.chat_id] = []
                chat_messages[msg.chat_id].append(msg)
            
            for chat_id, messages in chat_messages.items():
                chat_title = self.chats[chat_id]['title']
                f.write(f"\n📱 {chat_title} ({self.chats[chat_id]['type']})\n")
                f.write("-" * 60 + "\n")
                
                for msg in messages:
                    date_str = datetime.fromisoformat(msg.date).strftime('%Y-%m-%d %H:%M')
                    direction = "→" if msg.is_outgoing else "←"
                    f.write(f"[{date_str}] {direction} {msg.sender_name}: {msg.text}\n")
                
                f.write("\n")
        
        print(f"✅ Exported {len(self.messages)} messages to {filename}")
    
    def print_statistics(self):
        """Print message statistics"""
        print("\n📊 MESSAGE STATISTICS")
        print("=" * 50)
        print(f"Total Messages: {len(self.messages)}")
        print(f"Total Chats: {len(self.chats)}")
        
        # Chat type breakdown
        chat_types = {}
        for chat in self.chats.values():
            chat_type = chat['type']
            chat_types[chat_type] = chat_types.get(chat_type, 0) + 1
        
        print("\nChat Types:")
        for chat_type, count in chat_types.items():
            print(f"  {chat_type}: {count}")
        
        # Message count by chat
        chat_message_counts = {}
        for msg in self.messages:
            chat_title = msg.chat_title
            chat_message_counts[chat_title] = chat_message_counts.get(chat_title, 0) + 1
        
        print(f"\nTop 10 Chats by Message Count:")
        sorted_chats = sorted(chat_message_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (chat_title, count) in enumerate(sorted_chats[:10], 1):
            print(f"  {i}. {chat_title}: {count} messages")
        
        # Date range
        if self.messages:
            dates = [datetime.fromisoformat(msg.date) for msg in self.messages]
            earliest = min(dates)
            latest = max(dates)
            print(f"\nDate Range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}")
    
    async def interactive_mode(self):
        """Interactive mode for exploring messages"""
        print("\n🎯 INTERACTIVE MODE")
        print("=" * 30)
        
        while True:
            print("\nOptions:")
            print("1. Search messages by keyword")
            print("2. View messages from specific chat")
            print("3. Generate AI summary")
            print("4. Export messages")
            print("5. Show statistics")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                keyword = input("Enter keyword to search: ").strip()
                if keyword:
                    filtered = [msg for msg in self.messages if keyword.lower() in msg.text.lower()]
                    print(f"\nFound {len(filtered)} messages containing '{keyword}':")
                    for msg in filtered[:10]:  # Show first 10
                        date_str = datetime.fromisoformat(msg.date).strftime('%Y-%m-%d %H:%M')
                        print(f"[{date_str}] {msg.chat_title} - {msg.sender_name}: {msg.text[:100]}...")
            
            elif choice == "2":
                print("\nAvailable chats:")
                for i, (chat_id, chat_info) in enumerate(self.chats.items(), 1):
                    msg_count = len([msg for msg in self.messages if msg.chat_id == chat_id])
                    print(f"{i}. {chat_info['title']} ({chat_info['type']}) - {msg_count} messages")
                
                try:
                    chat_idx = int(input("Enter chat number: ")) - 1
                    chat_ids = list(self.chats.keys())
                    if 0 <= chat_idx < len(chat_ids):
                        chat_id = chat_ids[chat_idx]
                        chat_messages = [msg for msg in self.messages if msg.chat_id == chat_id]
                        print(f"\nMessages from {self.chats[chat_id]['title']}:")
                        for msg in chat_messages[:20]:  # Show first 20
                            date_str = datetime.fromisoformat(msg.date).strftime('%Y-%m-%d %H:%M')
                            direction = "→" if msg.is_outgoing else "←"
                            print(f"[{date_str}] {direction} {msg.sender_name}: {msg.text[:100]}...")
                except ValueError:
                    print("Invalid input")
            
            elif choice == "3":
                if self.ai_client:
                    summaries = await self.generate_summaries()
                    for chat_title, summary in summaries.items():
                        print(f"\n📝 Summary for {chat_title}:")
                        print(summary)
                else:
                    print("AI backend not available")
            
            elif choice == "4":
                print("\nExport formats:")
                print("1. JSON")
                print("2. CSV")
                print("3. TXT")
                export_choice = input("Choose format (1-3): ").strip()
                
                if export_choice == "1":
                    self.export_json()
                elif export_choice == "2":
                    self.export_csv()
                elif export_choice == "3":
                    self.export_txt()
            
            elif choice == "5":
                self.print_statistics()
            
            elif choice == "6":
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Read Telegram messages")
    parser.add_argument("--chats-only", action="store_true", help="Read only chat messages (no channels/groups)")
    parser.add_argument("--recent-days", type=int, help="Read messages from last N days")
    parser.add_argument("--export-format", choices=["json", "csv", "txt"], help="Export format")
    parser.add_argument("--keywords", nargs="+", help="Filter by keywords")
    parser.add_argument("--summarize", action="store_true", help="Generate AI summaries")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--limit", type=int, help="Limit number of messages per chat")
    
    args = parser.parse_args()
    
    try:
        # Create reader
        reader = TelegramMessageReader()
        
        # Connect to Telegram
        await reader.connect()
        
        # Get chats
        await reader.get_chats(chats_only=args.chats_only)
        
        # Read messages
        await reader.read_messages(
            limit=args.limit,
            recent_days=args.recent_days,
            keywords=args.keywords
        )
        
        # Print statistics
        reader.print_statistics()
        
        # Generate summaries if requested
        if args.summarize:
            summaries = await reader.generate_summaries()
            for chat_title, summary in summaries.items():
                print(f"\n📝 Summary for {chat_title}:")
                print(summary)
        
        # Export if requested
        if args.export_format:
            if args.export_format == "json":
                reader.export_json()
            elif args.export_format == "csv":
                reader.export_csv()
            elif args.export_format == "txt":
                reader.export_txt()
        
        # Interactive mode
        if args.interactive:
            await reader.interactive_mode()
        
        # Disconnect
        await reader.client.disconnect()
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 