from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.functions_classes import start_restart

tail_rt = Router()


@tail_rt.message()
async def tail_handler(message: Message, state: FSMContext):
    await start_restart(message=message, state=state)
