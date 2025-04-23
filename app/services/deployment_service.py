from fastapi import HTTPException
from ..utils.scenari_chain_server_portal import ScenariChainServerPortal
from app.config import config
import json
import logging
import zipfile
import shutil
import os

logger = logging.getLogger('uvicorn.error')


def load_json_config(file_path):
    """
    Charge un fichier JSON et retourne le dictionnaire correspondant.

    :param file_path: Chemin du fichier JSON à charger.
    :return: Dictionnaire contenant les mappages.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Erreur lors du chargement du fichier {file_path}: {e}")
        return {}


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
config_directory = os.path.join(project_root, 'config')
# Charger les mappages à partir des fichiers JSON
DEPLOYMENT_MANUALS_MAP = load_json_config(os.path.join(config_directory, 'deployment_manuals.json'))
SCENARI_MANUALS_MAP = load_json_config(os.path.join(config_directory, 'scenari_manuals.json'))
# Charger la liste des répertoires et fichiers à purger
items_to_purge_config = load_json_config(os.path.join(config_directory, 'items_to_purge.json'))
DIRECTORIES_TO_PURGE = items_to_purge_config.get("directories_to_purge", [])
FILES_TO_PURGE = items_to_purge_config.get("files_to_purge", [])


def deploy_manuals(manuals):
    logger.info(f"Deploying manuals: {manuals}")
    results = []

    for manual_enum in manuals:
        if isinstance(manual_enum, str):
            manual = manual_enum
        else:
            manual = manual_enum.value
        try:
            if manual not in SCENARI_MANUALS_MAP.keys():
                logger.info(f"Le manuel \'{manual}\' n'est pas dans la liste des fichiers de génération scenari")
                raise HTTPException(status_code=404,
                                    detail=f"Le manuel \'{manual}\' n'est pas dans la liste des fichiers de génération scenari")

            if manual not in DEPLOYMENT_MANUALS_MAP.keys():
                logger.info(f"Le manuel \'{manual}\' n'est pas dans la liste des fichiers du serveur de déploiement")
                raise HTTPException(status_code=404,
                                    detail=f"Le manuel \'{manual}\' n'est pas dans la liste des fichiers du serveur de déploiement")

            purge_directory(manual)
            generate_manual(SCENARI_MANUALS_MAP[manual])
            unzip_and_deploy(DEPLOYMENT_MANUALS_MAP[manual])

            results.append({"name": manual, "status": "success", "code": 200})
        except HTTPException as http_e:
            results.append({"name": manual, "status": "error", "code": http_e.status_code, "details": http_e.detail})
        except Exception as e:
            logger.error(f"Erreur lors du déploiement du manuel {manual}: {e}")
            results.append({"name": manual, "status": "error", "code": 500, "detail": str(e)})
    return results


def list_manuals():
    return list(DEPLOYMENT_MANUALS_MAP.keys())


def deploy_all_manuals():
    logger.info("Deploying all manuals")
    results = deploy_manuals(list(DEPLOYMENT_MANUALS_MAP.keys()))
    return {"deployments": results}


def purge_directory_list(manuals):
    logger.info(f"Purging manuals: {manuals}")
    results = []

    for manual_enum in manuals:
        try:
            if isinstance(manual_enum, str):
                manual = manual_enum
            else:
                manual = manual_enum.value
            purge_directory(manual)
            results.append({"name": manual, "status": "success", "code": 200})
        except Exception as e:
            logger.error(f"Erreur lors du déploiement du manuel {manual}: {e}")
            results.append({"name": manual, "status": "error", "code": 500, "detail": str(e)})
    return results

def purge_directory(manual):
    logger.info(f"Purging manual: {manual}")

    local_path = config.DEPLOYMENT_LOCAL_PATH + DEPLOYMENT_MANUALS_MAP[manual]
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
        if not os.path.exists(config.DEPLOYMENT_LOCAL_PATH + uri):
            os.makedirs(config.DEPLOYMENT_LOCAL_PATH + uri)
        # Dézipper l'archive
        with zipfile.ZipFile(config.GENERATION_ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(config.DEPLOYMENT_LOCAL_PATH + uri)
            logger.info(f"Fichier décompressé dans : {config.DEPLOYMENT_LOCAL_PATH + uri}")
        # Supprimer
        os.remove(config.GENERATION_ZIP_PATH)
    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier : {e}")


def generate_manual(pub_uri):
    scenari_portal = ScenariChainServerPortal()
    scenari_portal.generate(pub_uri)
