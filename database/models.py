from datetime import datetime
from typing import Annotated

from sqlalchemy import text, String, ForeignKey, PrimaryKeyConstraint, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

time_default_query = text("(now() at time zone 'utc')")
created_at = Annotated[datetime, mapped_column(server_default=time_default_query)]
updated_at = Annotated[datetime, mapped_column(server_default=time_default_query, onupdate=datetime.now())]


class Base(DeclarativeBase):
    def __repr__(self) -> str:
        columns = [f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()]
        return f"{self.__class__.__name__}({', '.join(columns)})"


class Music(Base):
    __tablename__ = "music"

    id = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(48))
    artist_id: Mapped[BigInteger] = mapped_column(ForeignKey("artists.id", onupdate="CASCADE", ondelete="CASCADE"))
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"))
    file_id: Mapped[str]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped['Users'] = relationship(back_populates='music')
    artist: Mapped['Artists'] = relationship(back_populates='music', lazy='joined')
    user_in_library: Mapped[list['Users']] = relationship(
        back_populates='music_in_library',
        secondary='library',
        lazy='joined'
    )


class Users(Base):
    __tablename__ = "users"

    id = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[created_at]

    music: Mapped[list['Music']] = relationship(back_populates='user', lazy='selectin')
    music_in_library: Mapped[list['Music']] = relationship(
        back_populates='user_in_library',
        secondary='library',
        lazy='joined'
    )


class Artists(Base):
    __tablename__ = "artists"

    id = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(48))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    music: Mapped[list['Music']] = relationship(back_populates='artist')


class Library(Base):
    __tablename__ = "library"

    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    music_id: Mapped[BigInteger] = mapped_column(ForeignKey('music.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at: Mapped[created_at]

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'music_id'),
    )
