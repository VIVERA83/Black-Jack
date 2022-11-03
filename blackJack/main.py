from aiohttp.web import run_app
from web.app import setup_app
app = setup_app()

if __name__ == "__main__":
    print(f"Start  http://127.0.0.1:8080/docs")
    run_app(app)
