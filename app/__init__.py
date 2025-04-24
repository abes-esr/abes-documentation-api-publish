import logging
import sys

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from .config import Config
from .routes import init_routes
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger('uvicorn.error')

def create_app():
    app = FastAPI(
        title="API de publication des manuels de l'ABES",
        docs_url=None,
        redoc_url=None,
        swagger_ui_parameters={
            "syntaxHighlight": {"theme": "agate", "activated": True},
            "showExtensions": False,
            "showCommonExtensions": False,
            "deepLinking": False
        }
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    # Setting a custom swagger html page ; custom css is passed into swagger-ui.css between modifAbes comments ; keep css through updates
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title,
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_css_url="/static/swagger-ui.css",
            swagger_js_url="/static/swagger-ui-bundle.js"
        )

    # Custom css file import
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Logging format
    stream_handler = logging.StreamHandler(sys.stdout)
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    init_routes(app)
    return app
