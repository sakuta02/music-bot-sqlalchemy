import asyncio
import environs

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import Redis, RedisStorage

from bot.handlers import *

env = environs.Env()
env.read_env()
bot_ = Bot(token=env('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
redis = Redis(host=env('REDIS_HOST'), password=env('REDIS_PASSWORD'))
storage = RedisStorage(redis=redis)


async def begin(bot: Bot, storage_: RedisStorage):
    dp = Dispatcher(storage=storage_)
    dp.include_routers(rt, upload_rt, library_rt, search_rt, song_rt)
    dp.include_router(tail_rt)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(begin(bot=bot_, storage_=storage))
