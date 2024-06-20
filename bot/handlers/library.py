from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from bot.dictionary import phrases, buttons
from bot.functions_classes import clear_blink, Pagination, get_song_by_id_and_check_owner
from bot.functions_classes import delete_from_lb, add_to_lb
from bot.keyboards import build_meta_keyboard
from bot.states import CommonStates

library_rt = Router()


@library_rt.message(F.text == buttons['library'], StateFilter(CommonStates.started))
async def send_library(message: Message):
    user_id, page = message.from_user.id, 0
    music, keyboard = await Pagination.music_pagination_in_library(page=page, user_id=message.from_user.id)
    if not music:
        await message.answer(text=phrases['library_no_results'], reply_markup=keyboard)
    else:
        await message.answer(text=phrases['library'].format(page + 1), reply_markup=keyboard)


@library_rt.callback_query(lambda call: call.data.startswith('lb_soon') or call.data.startswith('lb_back'))
async def send_library_page(call: CallbackQuery):
    command, page = call.strip('lb').split('-')
    page = int(page)

    if command == 'back':
        page = max(0, page - 2)

    music, keyboard = await Pagination.music_pagination_in_library(page=page, user_id=call.from_user.id,
                                                                   command=command)

    text = phrases['library'].format(page + 1)
    if not music:
        text += phrases['nothing_founded']

    await call.message.edit_text(text=text, reply_markup=keyboard)


@library_rt.callback_query(lambda call: call.data.startswith('delete-'))
@clear_blink
async def delete_from_library(call: CallbackQuery):
    user_id = call.from_user.id
    music_id, flag_operation = int(call.data.strip('delete-')), False
    value = await delete_from_lb(music_id=music_id, user_id=user_id)
    _, flag_owner = await get_song_by_id_and_check_owner(music_id, user_id)
    keyboard = await build_meta_keyboard(music_id=music_id, user_id=user_id, flag_owner=flag_owner)
    if value is True:
        await call.answer(text=phrases['delete_success'])
        await call.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await call.answer(text=phrases['delete_error'])


@library_rt.callback_query(lambda call: call.data.startswith('add-'))
@clear_blink
async def add_to_library(call: CallbackQuery):
    user_id = call.from_user.id
    music_id, flag_operation = int(call.data.strip('add-')), False
    value = await add_to_lb(music_id=music_id, user_id=user_id)
    _, flag_owner = await get_song_by_id_and_check_owner(music_id, user_id)
    keyboard = await build_meta_keyboard(music_id=music_id, user_id=user_id, flag_owner=flag_owner)
    if value is True:
        await call.answer(text=phrases['add_success'])
        await call.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await call.answer(text=phrases['add_error'])
