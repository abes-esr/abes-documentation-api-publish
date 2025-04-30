import os
from enum import Enum
from fastapi import APIRouter, Depends
from .__init__ import get_api_key
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from .services.deployment_service import deploy_manuals, list_manuals, deploy_all_manuals,  \
    load_json_config, config_directory, purge_directory_list
from .utils.misc import load_json_config, extract_paths


router = APIRouter()

config_data = load_json_config(os.path.join(config_directory, 'configuration_noms_chemins_manuels.json'))
DEPLOYMENT_MANUALS_MAP = extract_paths(config_data, "cheminDeploiement")
ManualEnum = Enum('ManualEnum', {key: key for key in DEPLOYMENT_MANUALS_MAP.keys()})

class Manual(BaseModel):
    name: str
    name: ManualEnum

@router.put("/deploy", tags=["Déployer"], dependencies=[Depends(get_api_key)])
async def deployer_un_ou_plusieurs_manuels(manuals: list[ManualEnum] = Query(...)):
    """
    Déploie un ou plusieurs manuels en purgeant les fichiers scenari.
    """
    results = deploy_manuals(manuals)
    return {"deployments": results}

@router.put("/deploy_all", tags=["Déployer"], dependencies=[Depends(get_api_key)])
async def deployer_tous_les_manuels():
    """
    Déploie tous les manuels en purgeant les fichiers scenari.
    """
    results = deploy_all_manuals()
    return {"deployments": results}

@router.delete("/purge", tags=["Purger"], dependencies=[Depends(get_api_key)])
async def purger_un_ou_plusieurs_manuels(manuals: list[ManualEnum] = Query(...)):
    """
    Purge les fichiers scenari des manuels en entrée. Liste des dossiers et fichiers scenari : skin, res, co, lib-md, meta, lib-sc, index.html
    """
    results = purge_directory_list(manuals)
    return {"purge": results}

@router.get("/liste", tags=["Lister"])
async def lister_les_manuels_disponibles_dans_l_API():
    """
    Donne la liste de tous les manuels de la base de données de l'API
    """
    return list_manuals()

def init_routes(app):
    app.include_router(router, prefix="/api")
