import os

from app import config
from app.utils.misc import load_json_config, extract_paths, create_workshop_list, logger

SCENARI_MANUALS_ARRAY = {}
SCENARI_DEPLOYMENT_ARRAY = {}
DIRECTORIES_TO_PURGE = []
FILES_TO_PURGE = []
CONFIG_DATA = {}
CONFIG_WORKSHOPS_LIST = {}
CONFIG_WORKSHOPS_ERROR_LIST = {}
GENERATOR_TYPES_CONFIG = {}
GENERATOR_TYPES_LIST = {}

def load_configuration_files():
    global SCENARI_MANUALS_ARRAY, SCENARI_DEPLOYMENT_ARRAY, DIRECTORIES_TO_PURGE, FILES_TO_PURGE, CONFIG_WORKSHOPS_LIST, CONFIG_WORKSHOPS_ERROR_LIST, GENERATOR_TYPES_CONFIG, GENERATOR_TYPES_LIST

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_directory = os.path.join(project_root, 'config')
    CONFIG_DATA = load_json_config(os.path.join(config_directory, 'configuration_noms_chemins_manuels.json'))
    create_workshop_list(CONFIG_DATA)
    CONFIG_WORKSHOPS_LIST = load_json_config(os.path.join(config_directory, 'scenari_ateliers.json'))
    CONFIG_WORKSHOPS_ERROR_LIST = load_json_config(os.path.join(config_directory, 'scenari_ateliers_erreurs.json'))
    GENERATOR_TYPES_CONFIG = load_json_config(os.path.join(config_directory, 'generator_types_codes.json'))
    GENERATOR_TYPES_LIST = extract_paths(CONFIG_DATA, "type", "atelier")

    for workshop, workshop_title in CONFIG_WORKSHOPS_LIST.items():
        SCENARI_MANUALS_ARRAY[workshop_title] = extract_paths(CONFIG_DATA, "cheminScenari", "atelier", workshop_title)
        SCENARI_DEPLOYMENT_ARRAY[workshop_title] = extract_paths(CONFIG_DATA, "cheminDeploiement", "atelier", workshop_title)

    # Check config file paths syntax
    for workshop_title in SCENARI_DEPLOYMENT_ARRAY:
        for manual_name in SCENARI_DEPLOYMENT_ARRAY[workshop_title]:
            deployment_path = SCENARI_DEPLOYMENT_ARRAY[workshop_title][manual_name]
            if deployment_path.startswith('/'):
                deployment_path = deployment_path[1:]
            SCENARI_DEPLOYMENT_ARRAY[workshop_title][manual_name] = os.path.join(config.DOCUMENTATION_API_PUBLISH_LOCAL_PATH, deployment_path)
        for manual_name in SCENARI_MANUALS_ARRAY[workshop_title]:
            scenari_path = SCENARI_MANUALS_ARRAY[workshop_title][manual_name]
            if not scenari_path.startswith('/'):
                SCENARI_MANUALS_ARRAY[workshop_title][manual_name] = os.path.join("/", scenari_path)


    items_to_purge_config = load_json_config(os.path.join(config_directory, 'items_to_purge.json'))
    DIRECTORIES_TO_PURGE = items_to_purge_config.get("directories_to_purge", [])
    FILES_TO_PURGE = items_to_purge_config.get("files_to_purge", [])