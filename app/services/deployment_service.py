from fastapi import HTTPException
from ..utils.scenari_chain_server_portal import ScenariChainServerPortal
from ..utils.misc import load_json_config, extract_paths
from app.config import config
import logging
import zipfile
import shutil
import os


def deploy_manuals(manuals, workshop_title):
    logger.info(f"Déploiement du manuel {manuals} de l'atelier {workshop_title}")
    results = []

    for manual_enum in manuals:
        if isinstance(manual_enum, str):
            manual = manual_enum
        else:
            manual = manual_enum.value
        try:
            scenari_manuals_map = SCENARI_MANUALS_ARRAY[workshop_title]
            deployment_manuals_map = SCENARY_DEPLOYMENT_ARRAY[workshop_title]
            if manual not in scenari_manuals_map.keys():
                logger.info(f"Le manuel \'{manual}\' n'est pas dans la liste des fichiers de génération scenari")
                raise HTTPException(status_code=404,
                                    detail=f"Le manuel \'{manual}\' n'est pas dans la liste des fichiers de génération scenari")

            if manual not in deployment_manuals_map.keys():
                logger.info(f"Le manuel \'{manual}\' n'est pas dans la liste des fichiers du serveur de déploiement")
                raise HTTPException(status_code=404,
                                    detail=f"Le manuel \'{manual}\' n'est pas dans la liste des fichiers du serveur de déploiement")

            if not os.path.isdir(config.DOCUMENTATION_API_PUBLISH_LOCAL_PATH + deployment_manuals_map[manual]):
                raise FileNotFoundError(
                    f"Le dossier '{config.DOCUMENTATION_API_PUBLISH_LOCAL_PATH + deployment_manuals_map[manual]}' n'existe pas.")

            generate_manual(scenari_manuals_map[manual], workshop_title)
            purge_directory(manual, workshop_title)
            unzip_and_deploy(deployment_manuals_map[manual])

            results.append({"name": manual, "workshop": workshop_title, "scenari_pub_path": scenari_manuals_map[manual], "deployment_path": deployment_manuals_map[manual], "status": "success", "code": 200})
        except HTTPException as http_e:
            results.append(
                {"name": manual, "workshop": workshop_title, "scenari_pub_path": scenari_manuals_map[manual], "deployment_path": deployment_manuals_map[manual], "status": "error", "code": http_e.status_code,
                 "details": http_e.detail})
        except Exception as e:
            logger.error(f"Erreur lors du déploiement du manuel {manual}: {e}")
            results.append({"name": manual, "workshop": workshop_title, "scenari_pub_path": scenari_manuals_map[manual], "deployment_path": deployment_manuals_map[manual], "status": "error", "code": 500,
                            "detail": str(e)})
    return results


def list_manuals(workshop_title):
    deployment_manuals_map = SCENARY_DEPLOYMENT_ARRAY[workshop_title]
    return list(deployment_manuals_map.keys())


def deploy_all_manuals(workshop_title):
    deployment_manuals_map = SCENARY_DEPLOYMENT_ARRAY[workshop_title]
    logger.info("Deploying all manuals")
    results = deploy_manuals(list(deployment_manuals_map.keys()), workshop_title)
    return {"deployments": results}


def purge_directory_list(manuals, workshop_title):
    logger.info(f"Purging manuals: {manuals}")
    results = []
    scenari_manuals_map = SCENARI_MANUALS_ARRAY[workshop_title]
    deployment_manuals_map = SCENARY_DEPLOYMENT_ARRAY[workshop_title]

    for manual_enum in manuals:
        try:
            if isinstance(manual_enum, str):
                manual = manual_enum
            else:
                manual = manual_enum.value
            purge_directory(manual, workshop_title)
            results.append({"name": manual, "scenari_pub_path": scenari_manuals_map[manual], "deployment_path": deployment_manuals_map[manual], "status": "success", "code": 200})
        except Exception as e:
            logger.error(f"Erreur lors du déploiement du manuel {manual}: {e}")
            results.append({"name": manual, "path": deployment_manuals_map[manual], "status": "error", "code": 500,
                            "detail": str(e)})
    return results


def purge_directory(manual, workshop_title):
    logger.info(f"Purging manual: {manual}")
    deployment_manuals_map = SCENARY_DEPLOYMENT_ARRAY[workshop_title]

    local_path = config.DOCUMENTATION_API_PUBLISH_LOCAL_PATH + deployment_manuals_map[manual]
    for directory in DIRECTORIES_TO_PURGE:
        directory_to_delete = local_path + directory
        logger.info(f"Suppression du dossier {directory_to_delete}")
        try:
            # Vérifie si le chemin existe
            if not os.path.exists(directory_to_delete):
                logger.info(f"Le dossier {directory_to_delete} n'existe pas.")
                continue

            # Supprime le répertoire et tout son contenu
            shutil.rmtree(directory_to_delete)
            logger.info(f"Le dossier {directory_to_delete} a été supprimé avec succès.")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du dossier {directory_to_delete}: {e}")
            raise RuntimeError(f"Erreur lors de la suppression du dossier {directory_to_delete}: {e}")
    for file in FILES_TO_PURGE:
        file_to_delete = local_path + file
        logger.info(f"Suppression du fichier {file_to_delete}")
        try:
            # Vérifie si le chemin existe
            if not os.path.exists(file_to_delete):
                logger.info(f"Le fichier {file_to_delete} n'existe pas.")
                continue

            # Supprime le répertoire et tout son contenu
            os.remove(file_to_delete)
            logger.info(f"Le fichier {file_to_delete} a été supprimé avec succès.")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier {file_to_delete}: {e}")
            raise RuntimeError(f"Erreur lors de la suppression du fichier {file_to_delete}: {e}")

    return {"success": True, "message": "Dossier purgé"}


def unzip_and_deploy(uri):
    try:
        # Dézipper l'archive
        with zipfile.ZipFile(config.DOCUMENTATION_API_PUBLISH_ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(config.DOCUMENTATION_API_PUBLISH_LOCAL_PATH + uri)
            logger.info(f"Fichier décompressé dans : {config.DOCUMENTATION_API_PUBLISH_LOCAL_PATH + uri}")
        # Supprimer
        os.remove(config.DOCUMENTATION_API_PUBLISH_ZIP_PATH)
    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier : {e}")
        raise


def generate_manual(pub_uri, workshop_title):
    scenari_portal = ScenariChainServerPortal(workshop_title)
    scenari_portal.generate(pub_uri)


logger = logging.getLogger('uvicorn.error')

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
config_directory = os.path.join(project_root, 'config')

config_workshops_list = load_json_config(os.path.join(config_directory, 'scenari_ateliers.json'))
config_data = load_json_config(os.path.join(config_directory, 'configuration_noms_chemins_manuels.json'))

SCENARI_MANUALS_ARRAY = {}
SCENARY_DEPLOYMENT_ARRAY = {}

for workshop, workshop_title in config_workshops_list.items():
    # load maps from JSON config file
    SCENARI_MANUALS_ARRAY[workshop_title] = extract_paths(config_data, "cheminScenari", "atelier", workshop_title)
    SCENARY_DEPLOYMENT_ARRAY[workshop_title] = extract_paths(config_data, "cheminDeploiement", "atelier", workshop_title)

# load files and directories names to purge
items_to_purge_config = load_json_config(os.path.join(config_directory, 'items_to_purge.json'))
DIRECTORIES_TO_PURGE = items_to_purge_config.get("directories_to_purge", [])
FILES_TO_PURGE = items_to_purge_config.get("files_to_purge", [])
