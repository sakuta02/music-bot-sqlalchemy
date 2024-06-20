from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.dictionary import phrases, buttons
from bot.functions_classes import Pagination, get_song_by_id_and_check_owner
from bot.keyboards import menu_solo_keyboard, build_meta_keyboard
from bot.states import CommonStates

search_rt = Router()


@search_rt.message(F.text == buttons['search'], StateFilter(CommonStates.started))
async def search(message: Message, state: FSMContext):
    await message.answer(text=phrases['search'], reply_markup=menu_solo_keyboard)
    await state.set_state(CommonStates.search)


@search_rt.message(StateFilter(CommonStates.search), F.text.startswith('#'))
async def search_song_by_tag(message: Message):
    music_id, user_id = int(message.text.strip('#')), int(message.from_user.id)
    song, flag_owner = await get_song_by_id_and_check_owner(music_id=music_id, user_id=user_id)
    if not song:
        await message.delete()
        await message.answer(phrases['song_error'])
    else:
        keyboard = await build_meta_keyboard(music_id=music_id, user_id=user_id, flag_owner=flag_owner)
        try:
            await message.answer_audio(audio=str(song.file_id),
                                       caption=phrases['caption'].format(song.title, song.artist.name, song.id),
                                       reply_markup=keyboard)
        except TelegramBadRequest:
            await message.answer(phrases['song_error'])


@search_rt.message(StateFilter(CommonStates.search), F.text)
async def send_start_music(message: Message):
    title, page = message.text, 0
    flag_music_exists, keyboard = await Pagination.music_pagination_in_search(title, page)
    phrase = phrases['results'].format(title, page + 1) if flag_music_exists else phrases['no_results'].format(title)
    await message.answer(text=phrase, reply_markup=keyboard)


@search_rt.callback_query(lambda call: call.data.startswith('soon') or call.data.startswith('back'))
async def send_music_page(call: CallbackQuery):
    command, title, page = call.data.split('-')
    page = int(page)

    if command == 'back':
        page = max(0, page - 2)

    flag_music_exists, keyboard = await Pagination.music_pagination_in_search(title=title, page=page, command=command)

    text = phrases['results'].format(title, page + 1)
    if not flag_music_exists:
        text += phrases['nothing_founded']

    await call.message.edit_text(text=text, reply_markup=keyboard)
