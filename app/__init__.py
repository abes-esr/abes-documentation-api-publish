from fastapi import FastAPI
from .config import Config
from .routes import init_routes
from fastapi.middleware.cors import CORSMiddleware

def create_app():
    app = FastAPI(title="documentation-api-publish")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    init_routes(app)
    return app