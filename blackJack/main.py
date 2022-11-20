from aiohttp.web import run_app
from web.app import setup_app

app = setup_app()

if __name__ == "__main__":
    run_app(app)
