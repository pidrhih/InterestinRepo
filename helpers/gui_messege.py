from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
import tkinter as tk
import logging

router: Router = Router()

@router.message(Command("msg"))
async def cmd_msg(message: Message):
    try:
        msg = message.text
        args = msg.split(" ")
        if len(args) != 3:
            await message.answer("Не указан текст и размер!!!")
        TextMSG = args[1]
        Len = args[2]
        root = tk.Tk()
        root.title(TextMSG)
        print(TextMSG, Len)

        # Указываем шрифт и размер
        label = tk.Label(
            root,
            text="Это текст увеличенного размера!",
            font=("Arial", int(Len))  # Шрифт и размер
        )
        label.pack(padx=20, pady=20)

        print("e")

        root.mainloop()
        print(TextMSG, Len)
        await message.answer("Сообщение было отправленно")
    except Exception as e:
        print(e)
        logging.error(e)
