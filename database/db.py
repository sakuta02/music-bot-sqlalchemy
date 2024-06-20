from environs import Env
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

env = Env()
env.read_env()

USER, PASSWORD, HOST, PORT, DATABASE = env('USER'), env('PASSWORD'), env('HOST'), env('PORT'), env('DATABASE')
URL = F"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

engine = create_async_engine(url=URL, echo=True, pool_size=5, max_overflow=5)
session_factory = async_sessionmaker(engine)
