from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.dictionary import buttons, phrases
from bot.functions_classes import get_artists_keyboard, safe_song, Pagination, clear_blink, delete_from_downloads
from bot.keyboards import menu_solo_keyboard, main_menu_keyboard
from bot.states import UploadStates, CommonStates

upload_rt = Router()


@upload_rt.message(F.text == buttons['upload'], StateFilter(CommonStates.started))
async def upload_song(message: Message, state: FSMContext):
    await message.answer(text=phrases['upload_file'], reply_markup=menu_solo_keyboard)
    await state.set_state(UploadStates.upload_file)


@upload_rt.message(StateFilter(UploadStates.upload_file), F.audio)
async def upload_file(message: Message, state: FSMContext):
    await message.answer(text=phrases['upload_title'], reply_markup=menu_solo_keyboard)
    await state.update_data({'file_id': message.audio.file_id})
    await state.set_state(UploadStates.enter_title)


@upload_rt.message(StateFilter(UploadStates.enter_title), F.text)
async def enter_title(message: Message, state: FSMContext):
    if len(message.text) < 48:
        await message.answer(text=phrases['upload_author'], reply_markup=menu_solo_keyboard)
        await state.update_data({'title': message.text})
        await state.set_state(UploadStates.enter_artist)
    else:
        await message.answer(text=phrases['length_constraint'])


@upload_rt.message(StateFilter(UploadStates.enter_artist), F.text)
async def enter_artist(message: Message, state: FSMContext):
    artist = message.text
    keyboard = await get_artists_keyboard(artist=artist)
    if not keyboard:
        data = await state.get_data()
        title, user_id, file_id = data['title'], message.from_user.id, data['file_id']
        value = await safe_song(title=title, user_id=user_id, file_id=file_id, artist=artist)
        if value is None:
            await message.answer(text=phrases['upload_success'], reply_markup=main_menu_keyboard)
            await state.set_state(CommonStates.started)
        else:
            await message.answer(text=phrases['length_constraint'])
    else:
        await state.update_data({'artist': message.text})
        await message.answer(text=phrases['authors'], reply_markup=keyboard)


@upload_rt.callback_query(StateFilter(UploadStates.enter_artist),
                          lambda call: call.data.startswith('artist-') or call.data == 'add_new_artist')
async def add_song(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    title, user_id, file_id = data['title'], call.from_user.id, data['file_id']
    if call.data == 'add_new_artist':
        artist = data['artist']
    else:
        artist = int(call.data.strip('artist-'))
    value = await safe_song(title=title, user_id=user_id, file_id=file_id, artist=artist)
    if value is None:
        await call.message.delete()
        await call.message.answer(text=phrases['upload_success'], reply_markup=main_menu_keyboard)
        await state.set_state(CommonStates.started)
    else:
        await call.message.answer(text=phrases['length_constraint'])


@upload_rt.message(F.text == buttons['my'], StateFilter(CommonStates.started))
async def send_downloads(message: Message):
    user_id, page = message.from_user.id, 0
    flag_music_exists, keyboard = await Pagination.music_pagination_in_downloads(page=page,
                                                                                 user_id=message.from_user.id)
    if not flag_music_exists:
        await message.answer(text=phrases['downloads_no_results'], reply_markup=keyboard)
    else:
        await message.answer(text=phrases['downloads'].format(page + 1), reply_markup=keyboard)


@upload_rt.callback_query(lambda call: call.data.startswith('dw_soon') or call.data.startswith('dw_back'))
async def send_library_page(call: CallbackQuery):
    command, page = call.data[3:].split('-')
    page = int(page)

    if command == 'back':
        page = max(0, page - 2)

    music, keyboard = await Pagination.music_pagination_in_downloads(page=page, user_id=call.from_user.id,
                                                                     command=command)

    text = phrases['downloads'].format(page + 1)
    if not music:
        text += phrases['nothing_founded']

    await call.message.edit_text(text=text, reply_markup=keyboard)


@upload_rt.callback_query(lambda call: call.data.startswith('dw_delete-'))
@clear_blink
async def manipulate_with_song_in_uploads(call: CallbackQuery):
    music_id, user_id = int(call.data.strip('dw_delete-')), call.from_user.id
    value = await delete_from_downloads(user_id=user_id, music_id=music_id)
    if value:
        await call.answer(text=phrases['delete_song_success'])
    else:
        await call.answer(text=phrases['delete_song_error'])
    await call.message.delete()
