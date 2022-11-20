import typing

from bj.views import (
    NewGame,
    NewRound,
    MovePlayer,
    RoundEnd,
    QuitGamePlayer,
    GetGameSession,
)

if typing.TYPE_CHECKING:
    from web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/new_game/", NewGame)
    app.router.add_view("/new_round/", NewRound)
    app.router.add_view("/move_player/", MovePlayer)
    app.router.add_view("/round_end/", RoundEnd)
    app.router.add_view("/quit_game_player/", QuitGamePlayer)
    app.router.add_view("/get_game_session_by_id/", GetGameSession)
