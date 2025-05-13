import os
import socket
import logging
import json

from app.utils.scenari_chain_server_portal import ScenariChainServerPortal

logger = logging.getLogger('uvicorn.error')


def is_local_environment():
    hostname = socket.gethostname()
    local_hostnames = ['localhost', '127.0.0.1', 'LAP-CDE']
    return hostname in local_hostnames


def load_json_config(file_path):
    # Loads a JSON file and returns the corresponding map
    try:
        with open(file_path, 'r',  encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Erreur lors du chargement du fichier {file_path}: {e}")
        return {}


def extract_paths(config_data, key_name, where_clause_key=None, where_clause_value=None):
    # Extracts paths for a given key and returns a map
    # if where_clause_key and where_clause_value are used, filters the config file on these values
    extracted_map = {}
    for entry in config_data:
        name = entry.get("name")
        paths = entry
        if where_clause_key is not None and where_clause_value is not None:
            if paths.get(where_clause_key) == where_clause_value:
                extracted_map[name] = paths.get(key_name, "")
        else:
            extracted_map[name] = paths.get(key_name, "")
    return extracted_map


def create_workshop_list(config_data):
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        config_file = os.path.join(project_root, 'config', 'scenari_ateliers.json')
        error_file = os.path.join(project_root, 'config', 'scenari_ateliers_erreurs.json')

        # Extract unique values of "atelier"
        unique_workshops = {entry["atelier"] for entry in config_data}
        sorted_workshops = sorted(unique_workshops)

        workshops_map = {}
        error_workshops_map = {}
        i = 1

        for index, workshop in enumerate(sorted_workshops):
            try:
                scenari_portal = ScenariChainServerPortal(workshop)
                wsp_code = scenari_portal.wsp_code

                if isinstance(wsp_code, str):
                    workshops_map[f"atelier{i}"] = workshop
                    i += 1
                else:
                    error_workshops_map[workshop] = "Code de l'atelier non valide ou non trouvé"
                    logger.info(f"Code de l'atelier non valide ou non trouvé pour {workshop}")
            except Exception as e:
                error_workshops_map[workshop] = f"Code de l'atelier non valide ou non trouvé: {e}"
                logger.info(f"Code de l'atelier non valide ou non trouvé pour {workshop}: {e}")

        # Save in files
        with open(config_file, 'w', encoding='utf-8') as json_file:
            json.dump(workshops_map, json_file, ensure_ascii=False, indent=4)
        logger.info(f"Le fichier {config_file} a été créé.")

        with open(error_file, 'w', encoding='utf-8') as json_file:
            json.dump(error_workshops_map, json_file, ensure_ascii=False, indent=4)
        logger.info(f"Le fichier {error_file} a été créé.")
    except Exception as e:
        logger.error(e)
