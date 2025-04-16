from fastapi import HTTPException
from ..utils.scenari_chain_server_portal import ScenariChainServerPortal
from app.config import config
import json
import logging
import zipfile
import shutil
import os

logger = logging.getLogger(__name__)

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
        print(f"Erreur lors du chargement du fichier {file_path}: {e}")
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
    print(f"Deploying manuals: {manuals}")

    for manual in manuals:
        if manual not in SCENARI_MANUALS_MAP.keys():
            raise HTTPException(status_code=404, detail=f"Le manuel \'{manual}\' n'est pas dans la liste des fichiers de génération scenari")

        if manual not in DEPLOYMENT_MANUALS_MAP.keys():
            raise HTTPException(status_code=404, detail=f"Le manuel \'{manual}\' n'est pas dans la liste des fichiers du serveur de déploiement")

        purge_directory(manual)
        generate_manual(SCENARI_MANUALS_MAP[manual])
        unzip_and_deploy(DEPLOYMENT_MANUALS_MAP[manual])

    return {"success": True, "message": "Deployment successful"}


def list_manuals():
    return list(DEPLOYMENT_MANUALS_MAP.keys())


def deploy_all_manuals():
    logger.info("Deploying all manuals")
    deploy_manuals(list(DEPLOYMENT_MANUALS_MAP.keys()))
    return {"success": True, "message": "Deployment successful"}


def purge_directory(manual):
    local_path = config.DEPLOYMENT_LOCAL_PATH + DEPLOYMENT_MANUALS_MAP[manual]
    for directory in DIRECTORIES_TO_PURGE:
        directory_to_delete = local_path + directory
        print(directory_to_delete)
        try:
            # Vérifie si le chemin existe
            if not os.path.exists(directory_to_delete):
                print(f"Directory {directory_to_delete} does not exist.")
                return

            # Supprime le répertoire et tout son contenu
            shutil.rmtree(directory_to_delete)
            print(f"Directory {directory_to_delete} removed successfully.")
        except Exception as e:
            print(f"Error removing directory {directory_to_delete}: {e}")

    for file in FILES_TO_PURGE:
        file_to_delete = local_path + file
        print(file_to_delete)
        try:
            # Vérifie si le chemin existe
            if not os.path.exists(file_to_delete):
                print(f"File {file_to_delete} does not exist.")
                return

            # Supprime le répertoire et tout son contenu
            os.remove(file_to_delete)
            print(f"File {file_to_delete} removed successfully.")
        except Exception as e:
            print(f"Error removing file {file_to_delete}: {e}")
    return {"success": True, "message": "Purge successful"}


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
    print(pub_uri)
    scenari_portal = ScenariChainServerPortal()
    scenari_portal.generate(pub_uri)
