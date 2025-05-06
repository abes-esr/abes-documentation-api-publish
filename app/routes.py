import os
from enum import Enum
from typing import Type

from fastapi import APIRouter, Depends
from .__init__ import get_api_key
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from .services.deployment_service import deploy_manuals, list_manuals, deploy_all_manuals,  \
    load_json_config, config_directory, purge_directory_list
from .utils.misc import load_json_config, extract_paths, create_workshop_list

router = APIRouter()

config_data = load_json_config(os.path.join(config_directory, 'configuration_noms_chemins_manuels.json'))
create_workshop_list(config_data)
config_workshops_list = load_json_config(os.path.join(config_directory, 'scenari_ateliers.json'))


####################################################################
# 1 tag per workshop
# routes are defined in methods so their attributes are fixed
for workshop, workshop_title in config_workshops_list.items():
    DEPLOYMENT_MANUALS_MAP = extract_paths(config_data, "cheminDeploiement", "atelier", workshop_title)
    ManualEnum = Enum(f'ManualEnum_{workshop}', {str(key): str(key) for key in DEPLOYMENT_MANUALS_MAP.keys()})
    class Manual(BaseModel):
        name: str
        name: ManualEnum

    def create_deploy_manuals_route(workshop: str, workshop_title: str):
        @router.put(f"/deploy/{workshop}", tags=[workshop_title], dependencies=[Depends(get_api_key)])
        async def deployer_un_ou_plusieurs_manuels(manuals: list[ManualEnum] = Query(...)):
            """
            Déploie un ou plusieurs manuels en purgeant les fichiers scenari.
            """
            results = deploy_manuals(manuals, workshop_title)
            return {"deployments": results}

    create_deploy_manuals_route(workshop, workshop_title)

    def create_deploy_all_manuals(workshop: str, workshop_title: str):
        @router.put(f"/deploy_all/{workshop}", tags=[workshop_title], dependencies=[Depends(get_api_key)])
        async def deployer_tous_les_manuels():
            """
            Déploie tous les manuels en purgeant les fichiers scenari.
            """
            results = deploy_all_manuals(workshop_title)
            return {"deployments": results}

    create_deploy_all_manuals(workshop, workshop_title)

    def create_delete_manuals(workshop: str, workshop_title: str):
        @router.delete(f"/purge/{workshop}", tags=[workshop_title], dependencies=[Depends(get_api_key)])
        async def purger_un_ou_plusieurs_manuels(manuals: list[ManualEnum] = Query(...)):
            """
            Purge les fichiers scenari des manuels en entrée. Liste des dossiers et fichiers scenari : skin, res, co, lib-md, meta, lib-sc, index.html
            """
            results = purge_directory_list(manuals, workshop_title)
            return {"purge": results}

    create_delete_manuals(workshop, workshop_title)

    def create_get_list(workshop: str, workshop_title: str):
        @router.get(f"/list /{workshop}", tags=[workshop_title])
        async def lister_les_manuels_disponibles_dans_l_API():
            """
            Donne la liste de tous les manuels de la base de données de l'API
            """
            return list_manuals(workshop_title)

    create_get_list(workshop, workshop_title)

def init_routes(app):
    app.include_router(router, prefix="/api")
