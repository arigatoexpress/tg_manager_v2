from telethon.sync import TelegramClient

api_id = "INSERT YOUR ID HERE"
api_hash = "INSERT YOUR ID HERE"

client = TelegramClient('session_name', api_id, api_hash)

with client:
    for dialog in client.iter_dialogs():
        print(dialog.name, dialog.id)
