from aiogram import Router
from aiogram.types import CallbackQuery
from bot.dictionary import phrases
from bot.functions_classes import clear_blink, get_song_by_id_and_check_owner, send_error_while_working_with_song
from bot.keyboards import build_meta_keyboard
from aiogram.exceptions import TelegramBadRequest

song_rt = Router()


@song_rt.callback_query(lambda call: call.data.startswith('id-'))
@clear_blink
async def send_song(call: CallbackQuery):
    music_id, user_id = int(call.data[3:]), call.from_user.id
    song, flag_owner = await get_song_by_id_and_check_owner(music_id, user_id)
    if not song:
        return await send_error_while_working_with_song(call=call)
    else:
        keyboard = await build_meta_keyboard(music_id=music_id, user_id=user_id, flag_owner=flag_owner)
        try:
            await call.message.answer_audio(audio=str(song.file_id),
                                            caption=phrases['caption'].format(song.title, song.artist.name, song.id),
                                            reply_markup=keyboard)
        except TelegramBadRequest:
            await call.message.answer(phrases['song_error'])
