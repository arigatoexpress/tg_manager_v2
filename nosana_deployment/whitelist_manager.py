#!/usr/bin/env python3
"""
Whitelist Manager for Team Access
=================================
Manage team member whitelist with comprehensive user information.
"""

import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class WhitelistUser:
    """Comprehensive user information for whitelist"""
    # Basic Information
    name: str
    email: str
    telegram_id: Optional[str] = None
    phone: Optional[str] = None
    
    # Access Control
    role: str = "user"  # admin, user, viewer
    access_level: str = "basic"  # basic, advanced, admin
    api_key: str = None
    is_active: bool = True
    
    # Security
    password_hash: Optional[str] = None
    last_password_change: Optional[str] = None
    failed_login_attempts: int = 0
    locked_until: Optional[str] = None
    
    # Usage Tracking
    created_at: str = None
    last_access: Optional[str] = None
    last_ip: Optional[str] = None
    total_logins: int = 0
    total_requests: int = 0
    
    # Team Information
    department: Optional[str] = None
    position: Optional[str] = None
    manager: Optional[str] = None
    team: Optional[str] = None
    
    # Contact Information
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    
    # Preferences
    notification_preferences: Dict[str, bool] = None
    ui_preferences: Dict[str, Any] = None
    
    # Audit Trail
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    modified_at: Optional[str] = None
    notes: Optional[str] = None

class WhitelistManager:
    """Manage comprehensive user whitelist"""
    
    def __init__(self, whitelist_file: str = "whitelist.json"):
        self.whitelist_file = whitelist_file
        self.users = self.load_whitelist()
        self.backup_dir = "whitelist_backups"
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def load_whitelist(self) -> List[Dict]:
        """Load whitelist from file"""
        try:
            if os.path.exists(self.whitelist_file):
                with open(self.whitelist_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading whitelist: {e}")
        return []
    
    def save_whitelist(self):
        """Save whitelist to file with backup"""
        try:
            # Create backup
            if os.path.exists(self.whitelist_file):
                backup_name = f"whitelist_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = os.path.join(self.backup_dir, backup_name)
                with open(self.whitelist_file, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
            
            # Save current whitelist
            with open(self.whitelist_file, 'w') as f:
                json.dump(self.users, f, indent=2)
                
        except Exception as e:
            print(f"Error saving whitelist: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password securely"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_hex = password_hash.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_hex
        except Exception:
            return False
    
    def add_user(self, user_data: Dict[str, Any], created_by: str = "system") -> bool:
        """Add new user to whitelist"""
        try:
            # Generate API key if not provided
            if not user_data.get("api_key"):
                user_data["api_key"] = f"wl_{secrets.token_urlsafe(24)}"
            
            # Hash password if provided
            if user_data.get("password"):
                user_data["password_hash"] = self.hash_password(user_data["password"])
                del user_data["password"]
            
            # Set creation timestamp
            user_data["created_at"] = datetime.now().isoformat()
            user_data["created_by"] = created_by
            
            # Initialize default values
            user_data.setdefault("notification_preferences", {
                "email": True,
                "telegram": True,
                "webhook": False
            })
            
            user_data.setdefault("ui_preferences", {
                "theme": "dark",
                "language": "en",
                "timezone": "UTC"
            })
            
            # Create user object
            user = WhitelistUser(**user_data)
            
            # Check for duplicates
            if self.get_user_by_email(user.email):
                print(f"User with email {user.email} already exists")
                return False
            
            # Add to whitelist
            self.users.append(asdict(user))
            self.save_whitelist()
            
            print(f"✅ Added user: {user.name} ({user.email})")
            return True
            
        except Exception as e:
            print(f"❌ Error adding user: {e}")
            return False
    
    def update_user(self, email: str, updates: Dict[str, Any], modified_by: str = "system") -> bool:
        """Update user information"""
        try:
            user = self.get_user_by_email(email)
            if not user:
                print(f"User {email} not found")
                return False
            
            # Update fields
            for key, value in updates.items():
                if key in user:
                    user[key] = value
            
            # Update metadata
            user["modified_at"] = datetime.now().isoformat()
            user["modified_by"] = modified_by
            
            # Hash password if updated
            if "password" in updates:
                user["password_hash"] = self.hash_password(updates["password"])
                user["last_password_change"] = datetime.now().isoformat()
                del user["password"]
            
            self.save_whitelist()
            print(f"✅ Updated user: {email}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating user: {e}")
            return False
    
    def remove_user(self, email: str) -> bool:
        """Remove user from whitelist"""
        try:
            original_count = len(self.users)
            self.users = [user for user in self.users if user["email"] != email]
            
            if len(self.users) < original_count:
                self.save_whitelist()
                print(f"✅ Removed user: {email}")
                return True
            else:
                print(f"User {email} not found")
                return False
                
        except Exception as e:
            print(f"❌ Error removing user: {e}")
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        for user in self.users:
            if user["email"] == email:
                return user
        return None
    
    def get_user_by_api_key(self, api_key: str) -> Optional[Dict]:
        """Get user by API key"""
        for user in self.users:
            if user.get("api_key") == api_key:
                return user
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        # Check if account is locked
        if user.get("locked_until"):
            lock_time = datetime.fromisoformat(user["locked_until"])
            if datetime.now() < lock_time:
                remaining = lock_time - datetime.now()
                print(f"Account locked for {remaining.seconds} more seconds")
                return None
        
        # Verify password
        if user.get("password_hash") and self.verify_password(password, user["password_hash"]):
            # Reset failed attempts
            user["failed_login_attempts"] = 0
            user["locked_until"] = None
            user["last_access"] = datetime.now().isoformat()
            user["total_logins"] += 1
            
            self.save_whitelist()
            return user
        else:
            # Increment failed attempts
            user["failed_login_attempts"] += 1
            
            # Lock account after 5 failed attempts
            if user["failed_login_attempts"] >= 5:
                user["locked_until"] = (datetime.now() + timedelta(minutes=30)).isoformat()
                print(f"Account locked for 30 minutes due to failed attempts")
            
            self.save_whitelist()
            return None
    
    def list_users(self, role_filter: Optional[str] = None) -> List[Dict]:
        """List all users with optional role filter"""
        if role_filter:
            return [user for user in self.users if user["role"] == role_filter]
        return self.users
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get whitelist statistics"""
        total_users = len(self.users)
        active_users = len([u for u in self.users if u["is_active"]])
        admin_users = len([u for u in self.users if u["role"] == "admin"])
        
        # Recent activity
        recent_users = []
        for user in self.users:
            if user.get("last_access"):
                last_access = datetime.fromisoformat(user["last_access"])
                if datetime.now() - last_access < timedelta(days=7):
                    recent_users.append(user["name"])
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "recent_users": recent_users,
            "recent_count": len(recent_users)
        }
    
    def export_whitelist(self, format: str = "json") -> str:
        """Export whitelist in various formats"""
        if format == "json":
            return json.dumps(self.users, indent=2)
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if self.users:
                writer = csv.DictWriter(output, fieldnames=self.users[0].keys())
                writer.writeheader()
                writer.writerows(self.users)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_whitelist(self, data: str, format: str = "json") -> bool:
        """Import whitelist from various formats"""
        try:
            if format == "json":
                imported_users = json.loads(data)
            elif format == "csv":
                import csv
                import io
                
                input_data = io.StringIO(data)
                reader = csv.DictReader(input_data)
                imported_users = list(reader)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Validate and add users
            for user_data in imported_users:
                self.add_user(user_data)
            
            print(f"✅ Imported {len(imported_users)} users")
            return True
            
        except Exception as e:
            print(f"❌ Error importing whitelist: {e}")
            return False
    
    def generate_whitelist_report(self) -> str:
        """Generate comprehensive whitelist report"""
        stats = self.get_user_stats()
        
        report = f"""
📋 WHITELIST REPORT
==================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 STATISTICS:
• Total Users: {stats['total_users']}
• Active Users: {stats['active_users']}
• Admin Users: {stats['admin_users']}
• Recent Activity (7 days): {stats['recent_count']}

👥 USER BREAKDOWN BY ROLE:
"""
        
        role_counts = {}
        for user in self.users:
            role = user["role"]
            role_counts[role] = role_counts.get(role, 0) + 1
        
        for role, count in role_counts.items():
            report += f"• {role.title()}: {count}\n"
        
        report += "\n🔐 SECURITY STATUS:\n"
        locked_users = [u for u in self.users if u.get("locked_until")]
        if locked_users:
            report += f"• Locked Accounts: {len(locked_users)}\n"
            for user in locked_users:
                report += f"  - {user['name']} ({user['email']})\n"
        else:
            report += "• No locked accounts\n"
        
        report += "\n📱 TELEGRAM INTEGRATION:\n"
        telegram_users = [u for u in self.users if u.get("telegram_id")]
        report += f"• Users with Telegram ID: {len(telegram_users)}/{stats['total_users']}\n"
        
        return report

def main():
    """Main whitelist management function"""
    print("🔐 WHITELIST MANAGER")
    print("=" * 50)
    
    manager = WhitelistManager()
    
    while True:
        print("\n📋 Available Options:")
        print("1. Add user")
        print("2. Update user")
        print("3. Remove user")
        print("4. List users")
        print("5. View statistics")
        print("6. Export whitelist")
        print("7. Import whitelist")
        print("8. Generate report")
        print("9. Exit")
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == "1":
            print("\n📝 Add New User:")
            name = input("Name: ")
            email = input("Email: ")
            role = input("Role (admin/user/viewer): ")
            password = input("Password (optional): ")
            telegram_id = input("Telegram ID (optional): ")
            
            user_data = {
                "name": name,
                "email": email,
                "role": role,
                "telegram_id": telegram_id if telegram_id else None
            }
            
            if password:
                user_data["password"] = password
            
            if manager.add_user(user_data):
                print("✅ User added successfully")
            else:
                print("❌ Failed to add user")
        
        elif choice == "2":
            email = input("Email to update: ")
            print("Enter new values (press Enter to skip):")
            
            updates = {}
            name = input("New name: ")
            if name:
                updates["name"] = name
            
            role = input("New role: ")
            if role:
                updates["role"] = role
            
            password = input("New password: ")
            if password:
                updates["password"] = password
            
            if updates:
                if manager.update_user(email, updates):
                    print("✅ User updated successfully")
                else:
                    print("❌ Failed to update user")
            else:
                print("No updates provided")
        
        elif choice == "3":
            email = input("Email to remove: ")
            if manager.remove_user(email):
                print("✅ User removed successfully")
            else:
                print("❌ Failed to remove user")
        
        elif choice == "4":
            role_filter = input("Filter by role (optional): ")
            users = manager.list_users(role_filter if role_filter else None)
            
            print(f"\n📋 Users ({len(users)}):")
            for user in users:
                status = "🔒" if user.get("locked_until") else "✅" if user["is_active"] else "❌"
                print(f"{status} {user['name']} ({user['email']}) - {user['role']}")
        
        elif choice == "5":
            stats = manager.get_user_stats()
            print("\n📊 Statistics:")
            print(f"Total Users: {stats['total_users']}")
            print(f"Active Users: {stats['active_users']}")
            print(f"Admin Users: {stats['admin_users']}")
            print(f"Recent Activity: {stats['recent_count']}")
        
        elif choice == "6":
            format_choice = input("Export format (json/csv): ").strip().lower()
            if format_choice in ["json", "csv"]:
                data = manager.export_whitelist(format_choice)
                filename = f"whitelist_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_choice}"
                
                with open(filename, 'w') as f:
                    f.write(data)
                
                print(f"✅ Exported to {filename}")
            else:
                print("❌ Invalid format")
        
        elif choice == "7":
            filename = input("Import file path: ")
            format_choice = input("File format (json/csv): ").strip().lower()
            
            try:
                with open(filename, 'r') as f:
                    data = f.read()
                
                if manager.import_whitelist(data, format_choice):
                    print("✅ Import successful")
                else:
                    print("❌ Import failed")
            except Exception as e:
                print(f"❌ Error reading file: {e}")
        
        elif choice == "8":
            report = manager.generate_whitelist_report()
            print(report)
            
            save = input("\nSave report to file? (y/n): ").strip().lower()
            if save == 'y':
                filename = f"whitelist_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w') as f:
                    f.write(report)
                print(f"✅ Report saved to {filename}")
        
        elif choice == "9":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main() 