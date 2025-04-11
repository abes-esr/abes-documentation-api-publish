from fastapi import FastAPI
from .config import Config
from .routes import init_routes

def create_app():
    app = FastAPI(title="Manuel Deployment Service")
    init_routes(app)
    return app
