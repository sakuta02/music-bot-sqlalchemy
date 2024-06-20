from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.dictionary import phrases, buttons
from bot.functions_classes import start_restart
from bot.keyboards import main_menu_keyboard
from bot.states import CommonStates

rt = Router()


@rt.message(Command(commands=['start', 'restart']))
async def start(message: Message, state: FSMContext):
    await start_restart(message=message, state=state)


@rt.message(Command(commands=['help']))
async def command_answer(message: Message):
    await message.answer(phrases[message.text.strip('/')])


@rt.message(lambda message: message.text in [buttons['menu'], buttons['cancel']])
async def exit_to_menu(message: Message, state: FSMContext):
    await message.answer(text=phrases['exit_to_menu'], reply_markup=main_menu_keyboard)
    await state.set_state(CommonStates.started)


@rt.callback_query(F.data == 'close')
async def close_tab(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(text=phrases['close'])


@rt.callback_query(F.data == 'menu')
async def exit_to_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text=phrases['exit_to_menu'], reply_markup=main_menu_keyboard)
    await state.set_state(CommonStates.started)
