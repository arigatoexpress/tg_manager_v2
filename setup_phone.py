#!/usr/bin/env python3
"""
Setup Phone Number for Telegram Message Reader
==============================================
Simple script to add your phone number to the .env file.
"""

import os
import re

def validate_phone(phone):
    """Validate phone number format"""
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Check if it starts with + and has reasonable length
    if not cleaned.startswith('+'):
        print("⚠️  Phone number should start with + (international format)")
        return False
    
    if len(cleaned) < 10 or len(cleaned) > 15:
        print("⚠️  Phone number seems too short or too long")
        return False
    
    return cleaned

def update_env_file(phone):
    """Update the .env file with the phone number"""
    env_file = ".env"
    
    # Read current .env file
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Check if TELEGRAM_PHONE already exists
    phone_line_index = None
    for i, line in enumerate(lines):
        if line.startswith('TELEGRAM_PHONE='):
            phone_line_index = i
            break
    
    # Create the new line
    new_line = f"TELEGRAM_PHONE={phone}\n"
    
    if phone_line_index is not None:
        # Update existing line
        lines[phone_line_index] = new_line
        print(f"✅ Updated existing TELEGRAM_PHONE line")
    else:
        # Add new line after TELEGRAM_API_HASH
        insert_index = None
        for i, line in enumerate(lines):
            if line.startswith('TELEGRAM_API_HASH='):
                insert_index = i + 1
                break
        
        if insert_index is not None:
            lines.insert(insert_index, new_line)
        else:
            # Add at the beginning if no API_HASH found
            lines.insert(0, new_line)
        
        print(f"✅ Added TELEGRAM_PHONE line")
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Phone number saved to {env_file}")

def main():
    """Main function"""
    print("📱 TELEGRAM PHONE NUMBER SETUP")
    print("=" * 40)
    
    print("\n💡 Instructions:")
    print("1. Enter your phone number in international format")
    print("2. Example: +1234567890 (US), +447911123456 (UK)")
    print("3. This will be used to authenticate with Telegram")
    print("4. Your phone number will be stored locally in .env file")
    
    while True:
        phone = input("\nEnter your phone number: ").strip()
        
        if not phone:
            print("❌ Phone number cannot be empty")
            continue
        
        validated_phone = validate_phone(phone)
        if not validated_phone:
            continue
        
        confirm = input(f"\nConfirm phone number: {validated_phone} (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            update_env_file(validated_phone)
            print(f"\n🎉 Phone number setup complete!")
            print(f"💡 You can now run: python test_message_reader.py")
            break
        else:
            print("🔄 Let's try again...")

if __name__ == "__main__":
    main() 