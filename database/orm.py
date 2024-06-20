from sqlalchemy import select, and_, func, desc
from sqlalchemy.exc import IntegrityError, NoResultFound, DBAPIError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import UnmappedInstanceError

from database.db import session_factory
from database.models import Artists, Music, Users, Library


class MusicOrm:
    @staticmethod
    async def delete_from_downloads(music_id: int, user_id: int) -> bool:
        async with session_factory() as session:
            try:
                query = select(Music).filter(and_(Music.id == music_id, Music.user_id == user_id))
                result = (await session.execute(query)).unique().scalar_one()

                await session.delete(result)
                await session.commit()
                return True
            except NoResultFound:
                return False

    @staticmethod
    async def add_song_and_artist(title: str, artist_name: str, user_id: int, file_id: str) -> bool | None:
        artist = Artists(name=artist_name)
        async with session_factory() as session:
            try:
                session.add(artist)
                await session.flush()
                song = Music(title=title, artist_id=artist.id, user_id=user_id, file_id=file_id)
                session.add(song)
                await session.commit()
            except DBAPIError:
                return False

    @staticmethod
    async def add_song_with_existing_artist(title: str, artist_id: int, user_id: int, file_id: str) -> bool | None:
        song = Music(title=title, artist_id=artist_id, user_id=user_id, file_id=file_id)
        async with session_factory() as session:
            try:
                session.add(song)
                await session.commit()
            except DBAPIError:
                return False

    @staticmethod
    async def get_songs_page_by_title(title: str, page: int) -> list[Music]:
        async with session_factory() as session:
            query = select(Music).where(Music.title.icontains(title)).limit(10).offset(page * 10).options(
                joinedload(Music.artist))
            result = sorted(
                (await session.execute(query))
                .unique().scalars().all(),
                key=lambda song: -len(song.user_in_library)
            )
            return result

    @staticmethod
    async def get_song_by_id(id_: int) -> Music:
        async with session_factory() as session:
            result = await session.get(Music, id_)
            return result


class ArtistsOrm:

    @staticmethod
    async def add_artist(name: str) -> None:
        artist = Artists(name=name)
        async with session_factory() as session:
            session.add(artist)
            await session.commit()

    @staticmethod
    async def get_artists_by_name(name: str) -> list[tuple[int, str]]:
        async with session_factory() as session:
            query = (select(Artists.id, Artists.name, func.count(Artists.id).label('amount'))
                     .where(Artists.name.icontains(name))
                     .join(Music, Music.artist_id == Artists.id, isouter=True)
                     .group_by(Artists.id)
                     .order_by(desc('amount'))
                     .limit(3))
            result = await session.execute(query)
            return result.all()

    @staticmethod
    async def get_artist_by_id(id_: int) -> Artists:
        async with session_factory() as session:
            artist = await session.get(Artists, id_)
            return artist


class UsersOrm:

    @staticmethod
    async def add_user(user_id: int) -> bool:
        async with session_factory() as session:
            try:
                user = Users(id=user_id)
                session.add(user)
                await session.commit()
                return True
            except IntegrityError:
                return False

    @staticmethod
    async def get_user(user_id: int) -> Users:
        async with session_factory() as session:
            result = await session.get(Users, user_id)
            return result


class LibraryOrm:

    @staticmethod
    async def add_to_library(music_id: int, user_id: int) -> bool:
        async with session_factory() as session:
            try:
                lb = Library(music_id=music_id, user_id=user_id)
                session.add(lb)
                await session.commit()
                return True
            except IntegrityError as ex:
                return False

    @staticmethod
    async def delete_from_library(music_id: int, user_id: int) -> bool:
        async with session_factory() as session:
            try:
                await session.get(Music, music_id)
                query = select(Library).filter_by(music_id=music_id, user_id=user_id)
                library_object = (await session.execute(query)).scalars().first()
                await session.delete(library_object)
                await session.commit()
                return True
            except NoResultFound:
                return False
            except UnmappedInstanceError:
                return False

    @staticmethod
    async def check_library(music_id: int, user_id: int) -> bool:
        async with session_factory() as session:
            query = select(Library).filter_by(music_id=music_id, user_id=user_id)
            library_object = (await session.execute(query)).first()
            return not bool(library_object)
