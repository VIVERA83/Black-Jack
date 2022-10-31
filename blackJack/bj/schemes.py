from typing import Optional
from marshmallow import EXCLUDE, Schema, fields, post_load

from bj.models import GameSessionModel, PlayerModel
from bj.dc import Content, GameSessionId, PlayerData, objects


class BaseSchema(Schema):
    __model__ = Optional[objects]

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


class ContentSchema(BaseSchema):
    __model__ = Content

    players_id = fields.List(fields.Int(), required=False)
    count_deck = fields.Int(required=False)
    initial_balance = fields.Int(required=False)


class GameSessionIdSchema(BaseSchema):
    __model__ = GameSessionId

    game_session_id = fields.Int(required=True)


class PlayerDataSchema(BaseSchema):
    __model__ = PlayerData

    game_session_id = fields.Int(required=True)
    player_id = fields.Int(required=True)
    action = fields.String(required=False)
