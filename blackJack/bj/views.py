from http.client import BAD_REQUEST

from aiohttp_apispec import docs, request_schema, response_schema
from bj.schemes import GamePlaySchema, GameSessionSchema
from web.app import View
from web.middlewares import HTTP_ERROR_CODES
from web.utils import error_json_response, json_response


class BJTestView(View):
    @docs(tags=["bj"], summary="TestView", description="Проверка все что можно")
    @request_schema(GamePlaySchema)
    @response_schema(GameSessionSchema)
    async def post(self):
        try:
            response = await self.store.bj_game_play.gameplay(self.data)
        except ValueError as e:
            return error_json_response(
                message=e.args[0],
                http_status=BAD_REQUEST,
                status=HTTP_ERROR_CODES[BAD_REQUEST],
            )
        return json_response(data=GameSessionSchema(exclude=["deck"]).dump(response))
