import asyncio
import argparse
from telethon import TelegramClient, events, sync
from telethon.sessions import StringSession
from telethon.tl.types import InputPeerUser, InputPeerChat, InputPeerChannel
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.tl.functions.channels import DeleteChannelRequest
from telethon.tl.functions.messages import DeleteChatUserRequest
import time
import os
from datetime import datetime, timedelta

# Your creds – replace these placeholders with your actual shit. Get 'em from https://my.telegram.org/apps.
# DON'T FUCKING COMMIT THIS WITH REAL KEYS TO GIT – .gitignore this file if needed.
api_id = YOUR_API_ID_HERE  # e.g., 1234567 (integer, no quotes)
api_hash = 'YOUR_API_HASH_HERE'  # e.g., 'abcdef1234567890abcdef1234567890' (string)
phone = 'YOUR_PHONE_HERE'  # e.g., '+15551234567' (string, with +country code)
two_fa_password = 'YOUR_2FA_PASSWORD_HERE'  # If no 2FA, set to None or comment out the sign_in(password) line.

# Custom RSA keys and DC config – optional, comment out if not needed. Defaults work for most.
# If you have 'em from Telegram docs or errors, paste here.
# from telethon.network import ConnectionTcpFull
# from telethon import connection
# import rsa

# pubkey1 = rsa.PublicKey.load_pkcs1("""YOUR_FIRST_PUBLIC_KEY_HERE""".encode('utf-8'))
# pubkey2 = rsa.PublicKey.load_pkcs1("""YOUR_SECOND_PUBLIC_KEY_HERE""".encode('utf-8'))

# custom_dc = (YOUR_DC_ID_HERE, 'YOUR_DC_IP_HERE', YOUR_DC_PORT_HERE)  # e.g., (2, '149.154.167.50', 443)

# Session file – saves login. Delete after use for security.
session_file = 'nuker.session'

async def main(client, args):
    print("Logged in. Scanning for targets.")
    
    # Get all dialogs.
    dialogs = await client.get_dialogs()
    
    # Filter based on args.target.
    if args.target == 'user':
        target_dialogs = [d for d in dialogs if d.is_user and not d.entity.bot]
    elif args.target == 'group':
        target_dialogs = [d for d in dialogs if d.is_group]
    elif args.target == 'channel':
        target_dialogs = [d for d in dialogs if d.is_channel]
    elif args.target == 'all':
        target_dialogs = [d for d in dialogs if d.is_user and not d.entity.bot or d.is_group or d.is_channel]
    else:
        raise ValueError("Invalid target type. Use 'user', 'group', 'channel', or 'all'.")
    
    total_targets = len(target_dialogs)
    print(f"Found {total_targets} {args.target} targets. Nuking messages and entities one by one.")
    
    for idx, dialog in enumerate(target_dialogs, 1):
        peer = dialog.entity
        chat_id = peer.id
        access_hash = peer.access_hash if hasattr(peer, 'access_hash') else 0
        
        if dialog.is_user:
            input_peer = InputPeerUser(chat_id, access_hash)
        elif dialog.is_group:
            input_peer = InputPeerChat(chat_id)
        elif dialog.is_channel:
            input_peer = InputPeerChannel(chat_id, access_hash)
        
        print(f"[{idx}/{total_targets}] Nuking {args.target} with ID {chat_id}.")
        
        # Delete messages with optional time filter.
        try:
            min_date = datetime.now() - timedelta(days=args.older_than) if args.older_than > 0 else None
            async for message in client.iter_messages(input_peer, from_user='me', limit=None, min_date=min_date):
                try:
                    await message.delete(revoke=True)  # Delete for everyone if possible.
                except FloodWaitError as e:
                    print(f"Flood wait: Sleeping {e.seconds} seconds.")
                    time.sleep(e.seconds)
                except Exception as e:
                    print(f"Skip message {message.id}: {e}")
        except Exception as e:
            print(f"Error scanning messages in {chat_id}: {e}")
        
        # Delete/leave the entity if flagged.
        if args.delete_entity:
            try:
                if dialog.is_user:
                    await client.delete_dialog(input_peer)
                elif dialog.is_group:
                    await client(DeleteChatUserRequest(chat_id=chat_id, user_id='me'))
                elif dialog.is_channel:
                    if peer.creator or peer.admin_rights:  # Only if owner/admin.
                        await client(DeleteChannelRequest(input_peer))
                    else:
                        await client.edit_folder(input_peer, folder=0)  # Unsubscribe if not admin.
                print(f"Entity {chat_id} deleted/left.")
            except Exception as e:
                print(f"Failed to delete/leave {chat_id}: {e}. You may need admin rights.")
    
    print(f"All {args.target} targets nuked. Clean slate achieved.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Telegram Nuker: Wipe messages and entities.")
    parser.add_argument('--target', type=str, default='user', choices=['user', 'group', 'channel', 'all'],
                        help="Target type: 'user' (DMs), 'group', 'channel', or 'all'.")
    parser.add_argument('--delete-entity', action='store_true',
                        help="Delete/leave the conversation/group/channel after wiping messages.")
    parser.add_argument('--older-than', type=int, default=0,
                        help="Only nuke messages older than X days (0 for all).")
    
    args = parser.parse_args()
    
    # Set up client. Uncomment custom stuff if defaults fail.
    client = TelegramClient(
        session_file,
        api_id,
        api_hash,
        # connection=ConnectionTcpFull,  # For reliability.
        # proxy=None,  # e.g., ('socks5', 'localhost', 9050) for Tor.
        request_retries=10,
        connection_retries=5,
        device_model='Nuker Script',
        system_version='YOUR_OS_HERE',  # e.g., 'Win10' or 'Linux'
        app_version='1.0'
    )
    
    # Uncomment for custom RSA keys.
    # client._rsa_keys = [pubkey1, pubkey2]
    
    # Connect, with fallback to custom DC if set.
    with client:
        # Handle auth.
        if not client.is_user_authorized():
            client.send_code_request(phone)
            code = input('Enter the code Telegram sent you: ')
            try:
                client.sign_in(phone, code)
            except SessionPasswordNeededError:
                client.sign_in(password=two_fa_password)
        
        client.loop.run_until_complete(main(client, args))
    
    # Optional session purge.
    # os.remove(session_file)  # Uncomment to auto-delete.
