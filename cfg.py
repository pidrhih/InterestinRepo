from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

bot_token = ''

bot = Bot(
    token=bot_token,
    default=DefaultBotProperties(parse_mode="HTML")
)
