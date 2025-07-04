import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Security, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from app.config import config
from fastapi.middleware.cors import CORSMiddleware
from app.load_config import load_configuration_files
from app.utils.misc import copy_file_to_directory


# API key headers configuratoin
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
API_KEY = config.DOCUMENTATION_API_PUBLISH_API_KEY

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Erreur d'authentification.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load manuals configuration files
    # Launch order at startup
    load_configuration_files()
    from .routes import init_routes
    init_routes(app)
    yield


def create_app():
    app = FastAPI(
        lifespan=lifespan,
        root_path="/dashboard",
        prefix="/dashboard",
        title="API Scenari Publish",
        docs_url=None,
        redoc_url=None,
        swagger_ui_parameters={
            "tryItOutEnabled": True,
            "syntaxHighlight": {"theme": "agate", "activated": True},
            "showExtensions": False,
            "showCommonExtensions": False,
            "deepLinking": False,
        }
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


    #########################################################################################################################################
    # Setting a custom openapi.json
    @app.get("/dashboard/custom/openapi.json", include_in_schema=False)
    async def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema


    #########################################################################################################################################
    # Setting a custom swagger html page ; custom css is passed into swagger-ui.css between modifAbes comments ; keep css through updates
    @app.get("/dashboard/access", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/dashboard/custom/openapi.json",
            title=app.title,
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_css_url="/dashboard/static/swagger-ui.css",
            swagger_js_url="/dashboard/static/swagger-ui-bundle.js"
        )


    # Custom css file import
    app.mount("/dashboard/static", StaticFiles(directory="static"), name="static")

    # Logging format
    logger = logging.getLogger('uvicorn.error')
    logger.propagate = False
    logger.handlers = [] # Suppress existing logging handlers
    stream_handler = logging.StreamHandler(sys.stdout)
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    return app
