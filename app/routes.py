from enum import Enum
from .__init__ import get_api_key
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel

from .load_config import CONFIG_WORKSHOPS_LIST, SCENARI_DEPLOYMENT_ARRAY
from .services.deployment_service import deploy_manuals, list_manuals, deploy_all_manuals, purge_directory_list, \
    list_workshops, list_errors, check_workshop_name

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
        @router.put(f"/deploy/{workshop}", tags=[f"Atelier : {workshop_title}"], dependencies=[Depends(get_api_key)])
        async def publier_un_ou_plusieurs_manuels_scenari_de_cet_atelier (
                save: bool = Query(False, description="Sauvegarder une copie du manuel sur le serveur"),
                manuals: list[ManualEnum] = Query(...)
        ):
            """
            Génère un ou plusieurs manuels de l’atelier Scenari puis les déploie sur le serveur Documentation. Possibilité de sauvegarder un ou plusieurs manuels dans la foulée de l’opération de publication ou séparément.
            """
            results = deploy_manuals(manuals, workshop_title, save)
            return {"deployments": results}


    create_deploy_manuals_route(workshop, workshop_title)


    def create_deploy_all_manuals(workshop: str, workshop_title: str):
        @router.put(f"/deploy_all/{workshop}", tags=[f"Atelier : {workshop_title}"], dependencies=[Depends(get_api_key)])
        async def publier_tous_les_manuels_scenari_de_cet_atelier(
                save: bool = Query(False, description="Sauvegarder une copie du manuel sur le serveur")
        ):
            """
            Génère tous les manuels de l’atelier Scenari puis les déploie sur le serveur Documentation. Possibilité de sauvegarder tous les manuels dans la foulée de l’opération de publication ou séparément.
            """
            results = deploy_all_manuals(workshop_title, save)
            return {"deployments": results}


    create_deploy_all_manuals(workshop, workshop_title)


    def create_delete_manuals(workshop: str, workshop_title: str):
        @router.delete(f"/purge/{workshop}", tags=[f"Atelier : {workshop_title}"], dependencies=[Depends(get_api_key)])
        async def purger_du_serveur_un_ou_plusieurs_manuels_scenari_de_cet_atelier(manuals: list[ManualEnum] = Query(...)):
            """
            Purge des répertoires du serveur Documentation les manuels Scenari sélectionnés. Supprime uniquement les dossiers et fichiers constituant les manuels Scenari (skin, res, co, lib-md, meta, lib-sc, index.html) et ne purge pas les autres fichiers présents dans les répertoires.
            """
            results = purge_directory_list(manuals, workshop_title)
            return {"purge": results}


    create_delete_manuals(workshop, workshop_title)


    def create_get_list(workshop: str, workshop_title: str):
        @router.get(f"/list/{workshop}", tags=[f"Atelier : {workshop_title}"])
        async def lister_les_manuels_scenari_dans_le_fichier_de_configuration_pour_cet_atelier():
            """
            Donne la liste de tous les manuels Scenari renseignés dans le fichier de configuration de l’API pour cet atelier.
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

@router.get(f"/check_workshop_name", tags=["Ateliers disponibles"])
async def verifier_la_validite_du_nom_d_atelier(wsp_name: str = Query()):
    """
    Donne la liste des erreurs rencontrées lors du chargement du fichier de configuration configuration_noms_chemins_manuels.json
    """
    return check_workshop_name(wsp_name)


def init_routes(app):
    app.include_router(router, prefix="/api/v1")
