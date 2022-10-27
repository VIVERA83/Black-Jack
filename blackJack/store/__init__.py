import typing

from store.database.database import Database

if typing.TYPE_CHECKING:
    from blackJack.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from store.bj.bj_accessor import BJAccessor
        from store.bj.bj_game import BJGamePlay

        self.bj = BJAccessor(app)
        self.bj_game_play = BJGamePlay(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
