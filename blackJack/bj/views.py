from aiohttp_apispec import docs, request_schema, response_schema, querystring_schema
from bj.schemes import (
    GameSessionSchema,
    ContentSchema,
    GameSessionIdSchema,
    PlayerDataSchema,
)
from web.app import View
from web.utils import json_response


class NewGame(View):
    @docs(tags=["bj"], summary="Новая игра", description="Создание новой игры")
    @request_schema(ContentSchema)
    @response_schema(GameSessionSchema)
    async def post(self):
        response = await self.store.bj_game_play.new_game(self.data)
        return json_response(data=GameSessionSchema(exclude=["deck"]).dump(response))


class NewRound(View):
    @docs(
        tags=["bj"],
        summary="Новая раздача",
        description="Новая раздача, игра продолжается пока есть карты в колоде",
    )
    @request_schema(GameSessionIdSchema)
    @response_schema(GameSessionSchema)
    async def post(self):
        response = await self.store.bj_game_play.new_round(
            game_session_id=self.data.game_session_id
        )
        return json_response(data=GameSessionSchema(exclude=["deck"]).dump(response))


class MovePlayer(View):
    @docs(
        tags=["bj"],
        summary="Ход игрока",
        description="Действия игрока, может быть как `move player` - взять карту,"
        " остальные трактуются как пропуск хода",
    )
    @request_schema(PlayerDataSchema)
    @response_schema(GameSessionSchema)
    async def post(self):
        response = await self.store.bj_game_play.move_player(
            game_session_id=self.data.game_session_id,
            player_id=self.data.player_id,
            action=self.data.action,
        )
        return json_response(data=GameSessionSchema(exclude=["deck"]).dump(response))


class RoundEnd(View):
    @docs(
        tags=["bj"],
        summary="Партия окончена",
        description="Раздача окончена, подведение итогов раздачи",
    )
    @request_schema(GameSessionIdSchema)
    @response_schema(GameSessionSchema)
    async def post(self):
        response = await self.store.bj_game_play.round_end(
            game_session_id=self.data.game_session_id
        )
        return json_response(data=GameSessionSchema(exclude=["deck"]).dump(response))


class QuitGamePlayer(View):
    @docs(
        tags=["bj"],
        summary="выйти из игры",
        description="Выход игрока из игры, игра продолжиться без его участия",
    )
    @request_schema(PlayerDataSchema)
    @response_schema(GameSessionSchema)
    async def post(self):
        response = await self.store.bj_game_play.quit_game_player(
            game_session_id=self.data.game_session_id, player_id=self.data.player_id
        )
        return json_response(data=GameSessionSchema(exclude=["deck"]).dump(response))


class GetGameSession(View):
    @docs(
        tags=["bj"],
        summary="Получить игровую сессию",
        description="Получить игровую сессию по `id`",
    )
    @querystring_schema(GameSessionIdSchema)
    @response_schema(GameSessionSchema)
    async def get(self):
        response = await self.store.bj.get_game_session_by_id(self.data.game_session_id)
        return json_response(data=GameSessionSchema(exclude=["deck"]).dump(response))
