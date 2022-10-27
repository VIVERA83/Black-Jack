from dataclasses import asdict, dataclass, field
from typing import Optional, Union

from bj.models import GameSessionModel, PlayerModel
from marshmallow import EXCLUDE, Schema, fields, post_load

objects = Union[GameSessionModel, PlayerModel]


class BaseSchema(Schema):
    __model__ = Optional[dataclass]

    @post_load
    def make_object(self, data, **kwargs) -> objects:  # noqa
        return self.__model__(**data)

    class Meta:
        unknown = EXCLUDE
        ordered = True


class PlayerSchema(BaseSchema):
    __model__ = PlayerModel

    id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    balance = fields.Int(required=True)
    score = fields.Int(required=True)
    hand = fields.List(fields.Str(), required=True)
    status = fields.Str(required=True)


class GameSessionSchema(BaseSchema):
    __model__ = GameSessionModel

    id = fields.Int(required=False)
    index = fields.Int(required=False)
    current_user_vk_id = fields.Int(required=False)
    deck = fields.List(fields.Str, required=False)
    status_game = fields.Str(required=True)
    players = fields.List(fields.Nested(PlayerSchema()))
    players_list = fields.List(fields.Int())
    allowed_actions = fields.List(fields.Str())


@dataclass
class Content:
    players_id: list[int] = field(default_factory=list)
    count_deck: int = None
    initial_balance: int = None

    @property
    def dict(self) -> dict:
        return asdict(self)


@dataclass
class GamePlay:
    action: str = None
    content: Content = None
    game_session_id: int = None


@dataclass
class GameResponse:
    game_session: GameSessionModel


class ContentSchema(BaseSchema):
    __model__ = Content

    players_id = fields.List(fields.Int(), required=False)
    count_deck = fields.Int(required=False)
    initial_balance = fields.Int(required=False)


class GamePlaySchema(BaseSchema):
    __model__ = GamePlay

    action = fields.Str(load_default=None)
    game_session_id = fields.Int()
    content = fields.Nested(ContentSchema(), load_default=Content())


class GameResponseSchema(BaseSchema):
    __model__ = GameResponse

    game_session = fields.Nested(GameSessionSchema(), required=False)
