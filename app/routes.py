import os
from enum import Enum

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from .services.deployment_service import deploy_manuals, list_manuals, deploy_all_manuals,  \
    load_json_config, config_directory, purge_directory_list
import logging

router = APIRouter()

DEPLOYMENT_MANUALS_MAP = load_json_config(os.path.join(config_directory, 'deployment_manuals.json'))
ManualEnum = Enum('ManualEnum', {key: key for key in DEPLOYMENT_MANUALS_MAP.keys()})

class Manual(BaseModel):
    name: str
    name: ManualEnum

@router.get("/liste")
async def list_available_manuals():
    """
    Donne la liste de tous les manuels de la base de données de l'API
    """
    return list_manuals()


@router.put("/deploy")
async def deploy(manuals: list[ManualEnum] = Query(...)):
    """
    Déploie un ou plusieurs manuels en purgeant les fichiers scenari.
    """
    status = deploy_manuals(manuals)
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Deployment failed")
    return status

@router.put("/deploy_all")
async def deploy_all():
    """
    Déploie tous les manuels en purgeant les fichiers scenari.
    """
    status = deploy_all_manuals()
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Deployment failed")
    return status

@router.delete("/purge")
async def purge_directory(manuals: list[ManualEnum] = Query(...)):
    """
    Purge les fichiers scenari des manuels en entrée. Liste des dossiers et fichiers scenari : skin, res, co, lib-md, meta, lib-sc, index.html
    """
    status = purge_directory_list(manuals)
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Purge failed")
    return status

def init_routes(app):
    app.include_router(router, prefix="/api")
