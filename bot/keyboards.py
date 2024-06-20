from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardBuilder

from bot.dictionary import buttons
from database.orm import Music, LibraryOrm

main_menu_keyboard = ReplyKeyboardMarkup(row_width=2, keyboard=[
    [KeyboardButton(text=buttons['upload']),
     KeyboardButton(text=buttons['my']), ],
    [KeyboardButton(text=buttons['search']),
     KeyboardButton(text=buttons['library'])]
], resize_keyboard=True, one_time_keyboard=False)

keyboard_cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=buttons['cancel'])]],
                                      one_time_keyboard=True,
                                      resize_keyboard=True)

menu_solo_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=buttons['menu'])]],
                                         one_time_keyboard=True,
                                         resize_keyboard=True)

menu_inline_button = InlineKeyboardButton(text=buttons['menu'], callback_data='menu')
menu_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[menu_inline_button]])
close_inline_button = InlineKeyboardButton(text=buttons['close'], callback_data='close')
close_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[close_inline_button]])

'''Поиск песен'''


def build_songs_keyboard(music: list[Music], page: int, title: str, flag=None) -> InlineKeyboardMarkup:
    soon_button = InlineKeyboardButton(
        text=buttons['soon'],
        callback_data=f'soon-{title}-{page}')
    back_button = InlineKeyboardButton(
        text=buttons['back'],
        callback_data=f'back-{title}-{page}')
    return page_builder(soon_button=soon_button, back_button=back_button, music=music, flag=flag, page=page)


'''Песня'''


async def build_meta_keyboard(music_id: int, user_id: int, flag_owner: bool = None) -> InlineKeyboardMarkup:
    flag_in_library = await LibraryOrm.check_library(music_id, user_id)
    add_to_lb_button = InlineKeyboardButton(
        text=buttons['add_to_library'],
        callback_data=f'add-{music_id}')
    delete_from_lb_button = InlineKeyboardButton(
        text=buttons['delete_from_library'],
        callback_data=f'delete-{music_id}')
    delete_from_dw_button = InlineKeyboardButton(
        text=buttons['delete_from_downloads'],
        callback_data=f'dw_delete-{music_id}')
    builder = InlineKeyboardBuilder()
    builder.row(add_to_lb_button) if flag_in_library is True else builder.row(delete_from_lb_button)
    builder.row(delete_from_dw_button) if flag_owner else None
    return builder.as_markup()


'''Библиотека'''


def build_library_keyboard(music: list[Music], page: int, flag: bool = None) -> InlineKeyboardMarkup:
    soon_button = InlineKeyboardButton(
        text=buttons['soon'],
        callback_data=f'lb_soon-{page}')
    back_button = InlineKeyboardButton(
        text=buttons['back'],
        callback_data=f'lb_back-{page}')
    return page_builder(soon_button=soon_button, back_button=back_button, music=music, flag=flag, page=page)


'''Загрузки'''


def build_downloads_keyboard(music: list[Music], page: int, flag: bool = None) -> InlineKeyboardMarkup:
    soon_button = InlineKeyboardButton(
        text=buttons['soon'],
        callback_data=f'dw_soon-{page}')
    back_button = InlineKeyboardButton(
        text=buttons['back'],
        callback_data=f'dw_back-{page}')
    return page_builder(soon_button=soon_button, back_button=back_button, music=music, flag=flag, page=page)


'''Пагинация страниц'''


def page_builder(soon_button: InlineKeyboardButton, back_button: InlineKeyboardButton, music: list[Music], page: int,
                 flag: bool = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.adjust(1)
    for song in music:
        builder.row(InlineKeyboardButton(text=f"{song.artist.name} - {song.title}", callback_data=f"id-{song.id}"))

    if len(music) < 10 and page == 1:
        builder.row(close_inline_button)
    elif flag is True:
        builder.row(back_button, close_inline_button)
    elif flag is False or page == 1:
        builder.row(close_inline_button, soon_button)
    else:
        builder.row(back_button, soon_button)

    return builder.as_markup()


'''Артист'''


def build_artists_keyboard(artists: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.adjust(1)
    for artist in artists:
        builder.row(InlineKeyboardButton(text=artist[1], callback_data=f'artist-{artist[0]}'))
    add_new_button = InlineKeyboardButton(text=buttons['add_new'], callback_data=f'add_new_artist')
    builder.row(add_new_button)
    builder.row(menu_inline_button)
    return builder.as_markup()
