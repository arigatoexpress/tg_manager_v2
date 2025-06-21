#!/usr/bin/env python3
"""
Team Access Manager for Telegram Bot
====================================
Simple team access management for your Nosana deployment.
"""

import os
import json
import secrets
from datetime import datetime
from typing import Dict, List, Optional

class TeamAccessManager:
    """Manage team access to Telegram Manager Bot"""
    
    def __init__(self):
        self.members_file = "team_members.json"
        self.members = self.load_members()
    
    def load_members(self) -> List[Dict]:
        """Load team members from file"""
        try:
            if os.path.exists(self.members_file):
                with open(self.members_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading members: {e}")
        return []
    
    def save_members(self):
        """Save team members to file"""
        try:
            with open(self.members_file, 'w') as f:
                json.dump(self.members, f, indent=2)
        except Exception as e:
            print(f"Error saving members: {e}")
    
    def add_member(self, name: str, email: str, role: str, telegram_id: Optional[str] = None) -> bool:
        """Add new team member"""
        member = {
            "name": name,
            "email": email,
            "role": role,
            "telegram_id": telegram_id,
            "access_level": "basic" if role == "user" else "admin" if role == "admin" else "advanced",
            "created_at": datetime.now().isoformat(),
            "last_access": None,
            "api_key": secrets.token_urlsafe(24)
        }
        
        self.members.append(member)
        self.save_members()
        return True
    
    def remove_member(self, email: str) -> bool:
        """Remove team member"""
        self.members = [m for m in self.members if m["email"] != email]
        self.save_members()
        return True
    
    def authenticate_member(self, api_key: str) -> Optional[Dict]:
        """Authenticate team member"""
        for member in self.members:
            if member.get("api_key") == api_key:
                member["last_access"] = datetime.now().isoformat()
                self.save_members()
                return member
        return None
    
    def list_members(self):
        """List all team members"""
        print("\n📋 Team Members:")
        for member in self.members:
            print(f"  • {member['name']} ({member['email']}) - {member['role']}")
            print(f"    API Key: {member['api_key']}")
            print(f"    Last Access: {member['last_access'] or 'Never'}")
            print()
    
    def generate_access_instructions(self) -> str:
        """Generate access instructions for team"""
        instructions = f"""
🔐 TEAM ACCESS INSTRUCTIONS
===========================

Your Telegram Manager Bot is now secure and accessible to your team!

📋 TEAM MEMBERS ({len(self.members)}):
"""
        
        for member in self.members:
            instructions += f"""
👤 {member['name']} ({member['email']})
   Role: {member['role']}
   API Key: {member['api_key']}
   Access Level: {member['access_level']}
"""
        
        instructions += """

🔑 HOW TO ACCESS:

1. Bot Status Check:
   curl -H "X-API-Key: YOUR_API_KEY" https://your-nosana-instance.com/api/team/bot/status

2. Your Profile:
   curl -H "X-API-Key: YOUR_API_KEY" https://your-nosana-instance.com/api/team/profile

3. Admin Functions (Admin only):
   curl -H "X-API-Key: YOUR_API_KEY" https://your-nosana-instance.com/api/team/members

🌐 WEB ACCESS:
- Admin Panel: https://your-nosana-instance.com/admin
- Bot Dashboard: https://your-nosana-instance.com/dashboard

📱 TELEGRAM ACCESS:
- Your bot is accessible via Telegram
- Send /start to begin
- Use /help for commands

🔒 SECURITY NOTES:
- Keep your API key secure
- Don't share API keys
- Report suspicious activity
- Logs are monitored for security

📞 SUPPORT:
- Contact admin for access issues
- Check logs for troubleshooting
- Monitor bot status regularly
"""
        return instructions

def main():
    """Main team management function"""
    print("👥 TEAM ACCESS MANAGER")
    print("=" * 50)
    
    manager = TeamAccessManager()
    
    while True:
        print("\n📋 Available Options:")
        print("1. Add team member")
        print("2. List team members")
        print("3. Remove team member")
        print("4. Generate access instructions")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            name = input("Name: ")
            email = input("Email: ")
            role = input("Role (admin/user/viewer): ")
            telegram_id = input("Telegram ID (optional): ")
            
            if manager.add_member(name, email, role, telegram_id if telegram_id else None):
                print(f"✅ Added {name} ({email}) as {role}")
            else:
                print("❌ Failed to add member")
        
        elif choice == "2":
            manager.list_members()
        
        elif choice == "3":
            email = input("Email to remove: ")
            if manager.remove_member(email):
                print(f"✅ Removed {email}")
            else:
                print("❌ Failed to remove member")
        
        elif choice == "4":
            instructions = manager.generate_access_instructions()
            print(instructions)
            
            save = input("\nSave instructions to file? (y/n): ").strip().lower()
            if save == 'y':
                with open("team_access_instructions.txt", 'w') as f:
                    f.write(instructions)
                print("✅ Saved to team_access_instructions.txt")
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main() 