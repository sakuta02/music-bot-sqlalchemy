from functools import wraps

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext

from bot.states import CommonStates
from bot.dictionary import phrases
from bot.keyboards import build_artists_keyboard, build_downloads_keyboard, main_menu_keyboard
from bot.keyboards import build_songs_keyboard, close_inline_keyboard
from database.orm import MusicOrm, Music, UsersOrm, ArtistsOrm, LibraryOrm


class Pagination:
    @staticmethod
    async def pagination_for_library_and_downloads(music: list[Music], page: int, command: str):
        if not music and command == 'start':
            return music, close_inline_keyboard
        flag = None if music else (True if command == 'soon' else False)
        keyboard = build_downloads_keyboard(music=music, page=page + 1, flag=flag)
        return bool(music), keyboard

    @staticmethod
    async def music_pagination_in_search(title: str, page: int, command: str = 'start') -> (bool, InlineKeyboardMarkup):
        music = await MusicOrm.get_songs_page_by_title(title, page)
        if not music and command == 'start':
            return bool(music), close_inline_keyboard
        flag = None if music else (True if command == 'soon' else False)
        keyboard = build_songs_keyboard(music=music, page=page + 1, title=title, flag=flag)
        return bool(music), keyboard

    @staticmethod
    async def music_pagination_in_downloads(page: int, user_id: int, command: str = 'start') -> tuple[
            bool, InlineKeyboardMarkup]:
        user = await UsersOrm.get_user(user_id=user_id)
        music = user.music[page * 10: (page + 1) * 10]
        return await Pagination.pagination_for_library_and_downloads(music=music, page=page, command=command)

    @staticmethod
    async def music_pagination_in_library(page: int, user_id: int, command: str = 'start') -> tuple[
            bool, InlineKeyboardMarkup]:
        user = await UsersOrm.get_user(user_id=user_id)
        music = user.music_in_library[page * 10: (page + 1) * 10]
        return await Pagination.pagination_for_library_and_downloads(music=music,  page=page, command=command)


async def get_artists_keyboard(artist: str) -> InlineKeyboardMarkup | None:
    artists = await ArtistsOrm.get_artists_by_name(artist)
    if not artists:
        return None
    keyboard = build_artists_keyboard(artists)
    return keyboard


async def safe_song(user_id: int, title: str, artist: str | int, file_id: str) -> None:
    if isinstance(artist, str):
        value = await MusicOrm.add_song_and_artist(title=title, artist_name=artist, user_id=user_id, file_id=file_id)
    else:
        value = await MusicOrm.add_song_with_existing_artist(title=title, artist_id=artist, user_id=user_id, file_id=file_id)
    return value


async def get_song_by_id_and_check_owner(music_id: int, user_id: int) -> tuple[Music, bool]:
    song = await MusicOrm.get_song_by_id(music_id)
    if song is None:
        flag_owner = False
    else:
        flag_owner = song.user_id == user_id
    return song, flag_owner


async def send_error_while_working_with_song(call: CallbackQuery) -> None:
    await call.message.delete()
    await call.message.answer(phrases['song_error'])


async def delete_from_lb(user_id: int, music_id: int) -> bool:
    return await LibraryOrm.delete_from_library(music_id=music_id, user_id=user_id)


async def delete_from_downloads(user_id: int, music_id: int) -> bool:
    return await MusicOrm.delete_from_downloads(music_id=music_id, user_id=user_id)


async def add_to_lb(user_id: int, music_id: int) -> bool:
    return await LibraryOrm.add_to_library(music_id=music_id, user_id=user_id)


async def start_restart(message: Message, state: FSMContext):
    user_id = message.from_user.id
    value = await UsersOrm.add_user(user_id=user_id)
    if value:
        await message.answer(text=phrases['start'], reply_markup=main_menu_keyboard)
    else:
        await message.answer(text=phrases['restart'], reply_markup=main_menu_keyboard)
    await state.set_state(CommonStates.started)


def clear_blink(func):
    @wraps(func)
    async def wrapper(call: CallbackQuery, *args, **kwargs) -> None:
        await func(call, *args, **kwargs)
        await call.answer()

    return wrapper
