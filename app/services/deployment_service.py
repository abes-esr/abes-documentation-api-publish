from datetime import datetime

from fastapi import HTTPException
from app.load_config import SCENARI_MANUALS_ARRAY, SCENARI_DEPLOYMENT_ARRAY, DIRECTORIES_TO_PURGE, FILES_TO_PURGE, \
    CONFIG_WORKSHOPS_LIST, CONFIG_WORKSHOPS_ERROR_LIST
from ..utils.misc import find_files, is_file_in_list
from ..utils.scenari_chain_server_portal import ScenariChainServerPortal
from app.config import config
import logging
import zipfile
import shutil
import os


def deploy_manuals(manuals, workshop_title, save):
    results = []

    if not save:
        save = False

    scenari_manuals_map = SCENARI_MANUALS_ARRAY[workshop_title]
    deployment_manuals_map = SCENARI_DEPLOYMENT_ARRAY[workshop_title]

    for manual_enum in manuals:
        if isinstance(manual_enum, str):
            manual = manual_enum
        else:
            manual = manual_enum.value

        logger.info(f"Déploiement du manuel {manual} de l'atelier {workshop_title}")

        try:
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
            if save:
                backup_manual(manual)
            remove_zip()

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
    deployment_manuals_map = SCENARI_DEPLOYMENT_ARRAY[workshop_title]
    return sorted(list(deployment_manuals_map.keys()))

def list_workshops():
    return CONFIG_WORKSHOPS_LIST

def list_errors():
    return CONFIG_WORKSHOPS_ERROR_LIST

def deploy_all_manuals(workshop_title, save):
    deployment_manuals_map = SCENARI_DEPLOYMENT_ARRAY[workshop_title]
    logger.info("Deploying all manuals")
    results = deploy_manuals(list(deployment_manuals_map.keys()), workshop_title, save)
    return {"deployments": results}


def purge_directory_list(manuals, workshop_title):
    logger.info(f"Purge des manuels: {manuals}")
    results = []
    scenari_manuals_map = SCENARI_MANUALS_ARRAY[workshop_title]
    deployment_manuals_map = SCENARI_DEPLOYMENT_ARRAY[workshop_title]

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
    logger.info(f"Purge du manuel: {manual}")
    deployment_manuals_map = SCENARI_DEPLOYMENT_ARRAY[workshop_title]

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
            logger.info(f"Le dossier {directory_to_delete} a été purgé avec succès.")
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
            logger.info(f"Le fichier {file_to_delete} a été purgé avec succès.")
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
    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier : {e}")
        raise


def backup_manual(manual_name):
    try:
        now = datetime.now()
        formatted_time = now.strftime("_%Y-%m-%d_%H-%M-%S")

        kebab_case_name = manual_name.lower().replace(' ', '-')
        new_file_name = kebab_case_name + formatted_time + '.zip'
        new_file_path = config.DOCUMENTATION_API_PUBLISH_LOCAL_BACKUP_PATH + new_file_name

        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        shutil.copy2(config.DOCUMENTATION_API_PUBLISH_ZIP_PATH, new_file_path)
        logger.info(f"Sauvegarde réussie : {new_file_path}")
    except FileNotFoundError as e:
        logger.error(f"Fichier non trouvé : {config.DOCUMENTATION_API_PUBLISH_ZIP_PATH}")
        raise
    except PermissionError as e:
        logger.error(f"Permission refusée : {e}")
        raise
    except Exception as e:
        logger.error(f"Une erreur est survenue : {e}")
        raise

def remove_zip():
    try:
        os.remove(config.DOCUMENTATION_API_PUBLISH_ZIP_PATH)
    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier : {e}")
        raise


def generate_manual(pub_uri, workshop_title):
    scenari_portal = ScenariChainServerPortal(workshop_title)
    scenari_portal.generate(pub_uri)
    del scenari_portal


def check_workshop_name(workshop_name: str):
    scenari_portal = ScenariChainServerPortal(workshop_name)
    wsp_code = scenari_portal.wsp_code
    del scenari_portal
    if wsp_code:
        return wsp_code
    else:
        return f"L'API n'a pas trouvé l'atelier recherché : '{workshop_name}'"


logger = logging.getLogger('uvicorn.error')