import logging
import sys

from fastapi import FastAPI
from .config import Config
from .routes import init_routes
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger('uvicorn.error')

def create_app():
    app = FastAPI(title="API de publication des manuels de l'ABES", swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}})
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    init_routes(app)
    return app