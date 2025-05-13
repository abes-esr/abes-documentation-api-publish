from enum import Enum
from .__init__ import get_api_key
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel

from .load_config import CONFIG_WORKSHOPS_LIST, SCENARI_DEPLOYMENT_ARRAY
from .services.deployment_service import deploy_manuals, list_manuals, deploy_all_manuals, purge_directory_list, \
    list_workshops, list_errors

router = APIRouter()


####################################################################
# 1 tag per workshop
# routes are defined in methods so their attributes are fixed
for workshop, workshop_title in CONFIG_WORKSHOPS_LIST.items():
    deployment_manuals_map = SCENARI_DEPLOYMENT_ARRAY[workshop_title]
    ManualEnum = Enum(f'ManualEnum_{workshop}', {str(key): str(key) for key in sorted(deployment_manuals_map.keys())})


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
        @router.get(f"/list/{workshop}", tags=[workshop_title])
        async def lister_les_manuels_disponibles_dans_l_API():
            """
            Donne la liste de tous les manuels de la base de données de l'API
            """
            return list_manuals(workshop_title)


    create_get_list(workshop, workshop_title)


####################################################################
# Get the list of workshops
#
@router.get(f"/list/workshops", tags=["Ateliers disponibles"])
async def lister_les_ateliers_disponibles_dans_l_API():
    """
    Donne la liste de tous les ateliers et du nom de la route correspondante
    """
    return list_workshops()


####################################################################
# Get the list of configuration file loading errors
#
@router.get(f"/list/errors", tags=["Ateliers disponibles"])
async def lister_les_erreurs_au_chargement_du_fichier_de_configuration():
    """
    Donne la liste des erreurs rencontrées lors du chargement du fichier de configuration configuration_noms_chemins_manuels.json
    """
    return list_errors()


def init_routes(app):
    app.include_router(router, prefix="/api")
