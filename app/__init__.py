from fastapi import FastAPI
from .config import Config
from .routes import init_routes
from fastapi.middleware.cors import CORSMiddleware

def create_app():
    app = FastAPI(title="API de publication des manuels de l'ABES",swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}})
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    init_routes(app)
    return app