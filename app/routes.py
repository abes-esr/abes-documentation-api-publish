import os
from enum import Enum
import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from .services.deployment_service import deploy_manuals, list_manuals, deploy_all_manuals,  \
    load_json_config, config_directory, purge_directory_list

router = APIRouter()

DEPLOYMENT_MANUALS_MAP = load_json_config(os.path.join(config_directory, 'deployment_manuals.json'))
ManualEnum = Enum('ManualEnum', {key: key for key in DEPLOYMENT_MANUALS_MAP.keys()})

class Manual(BaseModel):
    name: str
    name: ManualEnum

@router.get("/liste", tags=["Lister"])
async def lister_les_manuels_disponibles_dans_l_API():
    """
    Donne la liste de tous les manuels de la base de données de l'API
    """
    return list_manuals()


@router.put("/deploy", tags=["Déployer"])
async def deployer_un_ou_plusieurs_manuels(manuals: list[ManualEnum] = Query(...)):
    """
    Déploie un ou plusieurs manuels en purgeant les fichiers scenari.
    """
    status = deploy_manuals(manuals)
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Erreur de déploiement")
    return status

@router.put("/deploy_all", tags=["Déployer"])
async def deployer_tous_les_manuels():
    """
    Déploie tous les manuels en purgeant les fichiers scenari.
    """
    status = deploy_all_manuals()
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Erreur de déploiement")
    return status

@router.delete("/purge", tags=["Purger"])
async def purger_un_ou_plusieurs_manuels(manuals: list[ManualEnum] = Query(...)):
    """
    Purge les fichiers scenari des manuels en entrée. Liste des dossiers et fichiers scenari : skin, res, co, lib-md, meta, lib-sc, index.html
    """
    status = purge_directory_list(manuals)
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression du manuel")
    return status

def init_routes(app):
    app.include_router(router, prefix="/api")
