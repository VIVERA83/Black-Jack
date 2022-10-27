import enum
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import ARRAY, TIMESTAMP, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from store.database.sqlalchemy_base import db

Card = str
Deck = list[Card]


class ResultEnum(enum.Enum):
    win: str = "win"
    lost: str = "loss"


class StatusGameEnum(enum.Enum):
    active: str = "active"
    finished: str = "finished"


class StatusPlayerEnum(enum.Enum):
    active: str = "active"
    lost: str = "lost"


@dataclass
class UserModel(db):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, nullable=False)
    vk_user_id: int = Column(Integer, nullable=False)

    scores: int = relationship("ScoresModel", backref="users", uselist=False)
    statistics_data: list["StaticsDataModel"] = relationship(
        "StaticsDataModel", backref="users", cascade="all, delete", passive_deletes=True
    )


@dataclass
class StaticsDataModel(db):
    __tablename__ = "staticsDatas"

    id: int = Column(Integer, primary_key=True, nullable=False)
    result: str = Column(Enum(ResultEnum))
    score: int = Column(Integer, nullable=True, default=int)
    create = Column(TIMESTAMP, nullable=False, default=datetime.now)
    user_id: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


@dataclass
class ScoresModel(db):
    __tablename__ = "scores"

    id: int = Column(Integer, primary_key=True, nullable=False)
    user_id: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    scores: int = Column(Integer, nullable=False, default=int)


@dataclass
class GameSessionModel(db):
    __tablename__ = "game_sessions"

    id: int = Column(Integer, primary_key=True, nullable=False)
    index: int = Column(Integer, nullable=False)
    current_user_vk_id: int = Column(Integer)
    deck: Deck = Column(ARRAY(String))
    status_game: str = Column(Enum(StatusGameEnum))
    players: list["PlayerModel"] = relationship(
        "PlayerModel",
        backref="game_sessions",
        cascade="all, delete",
        passive_deletes=True,
    )
    players_list: list[int] = Column(ARRAY(Integer))
    allowed_actions: list[str] = Column(ARRAY(String))


@dataclass
class PlayerModel(db):
    __tablename__ = "players"

    id: int = Column(Integer, primary_key=True, nullable=False)
    user_id: int = Column(Integer, nullable=False)
    balance: int = Column(Integer, nullable=False)
    score: int = Column(Integer, nullable=False, default=int)
    hand: Deck = Column(ARRAY(String))
    status: str = Column(Enum(StatusPlayerEnum))

    game_session_id: int = Column(
        Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False
    )
