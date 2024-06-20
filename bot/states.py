from aiogram.fsm.state import StatesGroup, State


class CommonStates(StatesGroup):
    search = State()
    library = State()
    upload = State()
    started = State()


class UploadStates(StatesGroup):
    enter_artist = State()
    enter_title = State()
    upload_file = State()

