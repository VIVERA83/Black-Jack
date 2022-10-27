from aiohttp.web_app import Application


def setup_routes(app: Application):
    from bj.routes import setup_routes as bj_setup_routes

    bj_setup_routes(app)
