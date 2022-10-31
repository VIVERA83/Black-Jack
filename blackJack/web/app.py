from typing import Optional

from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec
from config import Config
from dotenv import load_dotenv
from store import Store, setup_store
from store.database.database import Database
from web.middlewares import setup_middlewares
from web.routes import setup_routes
from bj.schemes import objects


class Application(web.Application):
    config: Optional["Config"] = None
    store: Optional["Store"] = None
    database: Optional["Database"] = None


class Request(web.Request):
    @property
    def app(self) -> Application:
        return super().app()


class View(web.View):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def database(self):
        return self.request.app.database

    @property
    def store(self) -> "Store":
        return self.request.app.store

    @property
    def data(self) -> "objects":
        return self.request.get("data", {})


app = Application()
load_dotenv()


def setup_app() -> "Application":
    app.config = Config()
    setup_routes(app)
    setup_aiohttp_apispec(
        app, title="Black Jack", url="/api/docs/swagger.json", swagger_path="/docs"
    )
    setup_middlewares(app)
    setup_store(app)
    return app
