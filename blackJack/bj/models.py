import enum
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import ARRAY, Column, Enum, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from store.database.sqlalchemy_base import db


class StatusGameEnum(enum.Enum):
    active: str = "active"
    finished: str = "finished"


class StatusPlayerEnum(enum.Enum):
    active: str = "active"
    lost: str = "lost"


@dataclass
class GameSessionModel(db):
    __tablename__ = "game_sessions"  # noqa

    id: int = Column(Integer, primary_key=True, nullable=False)
    index: int = Column(Integer, nullable=False)
    current_user_vk_id: int = Column(Integer)
    deck: list[str] = Column(ARRAY(String))
    status_game: str = Column(Enum(StatusGameEnum))
    players: list["PlayerModel"] = relationship(
        "PlayerModel",
        backref="game_sessions",
        cascade="all, delete",
        passive_deletes=True,
    )
    players_list: list[int] = Column(ARRAY(Integer))
    allowed_actions: list[str] = Column(ARRAY(String))
    modification: datetime = Column(TIMESTAMP, default=datetime.now())


@dataclass
class PlayerModel(db):
    __tablename__ = "players"  # noqa

    id: int = Column(Integer, primary_key=True, nullable=False)
    user_id: int = Column(Integer, nullable=False)
    balance: int = Column(Integer, nullable=False)
    score: int = Column(Integer, nullable=False, default=int)
    hand: list[str] = Column(ARRAY(String))
    status: str = Column(Enum(StatusPlayerEnum))

    game_session_id: int = Column(
        Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False
    )
