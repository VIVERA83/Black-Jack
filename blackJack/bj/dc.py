from typing import Union, Type
from dataclasses import asdict, dataclass, field

objects = Union[
    Type["GameSessionId"],
    Type["GameSessionModel"],
    Type["PlayerModel"],
    Type["PlayerData"],
]


@dataclass
class Content:
    players_id: list[int] = field(default_factory=list)
    count_deck: int = None
    initial_balance: int = None

    @property
    def dict(self) -> dict:
        return asdict(self)


@dataclass
class GameSessionId:
    game_session_id: int


@dataclass
class PlayerData(GameSessionId):
    player_id: int
    action: str = None
