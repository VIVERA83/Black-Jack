import typing

from bj.views import BJTestView

if typing.TYPE_CHECKING:
    from web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/bj.test/", BJTestView)
