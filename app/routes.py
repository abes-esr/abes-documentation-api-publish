import os
from enum import Enum

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from .services.deployment_service import deploy_manuals, list_manuals, deploy_all_manuals, purge_directory, \
    load_json_config, config_directory
import logging

router = APIRouter()

DEPLOYMENT_MANUALS_MAP = load_json_config(os.path.join(config_directory, 'deployment_manuals.json'))
ManualEnum = Enum('ManualEnum', {key: key for key in DEPLOYMENT_MANUALS_MAP.keys()})

class Manual(BaseModel):
    name: str
    name: ManualEnum

@router.get("/liste")
async def list_available_manuals():
    return list_manuals()


@router.put("/deploy")
async def deploy(manual: list[ManualEnum] = Query(...)):
    logging.info("{str(manual)}")
    status = deploy_manuals(manual)
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Deployment failed")
    return status

@router.put("/deploy_all")
async def deploy_all():
    status = deploy_all_manuals()
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Deployment failed")
    return status

@router.delete("/purge_directory")
async def purge_dir(manuel: str = Query(...)):
    status = purge_directory(manuel)
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Purge failed")
    return status

def init_routes(app):
    app.include_router(router, prefix="/api")
