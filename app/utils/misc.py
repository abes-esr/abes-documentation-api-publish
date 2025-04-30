import socket
import logging
import json


logger = logging.getLogger('uvicorn.error')


def is_local_environment():
    hostname = socket.gethostname()
    local_hostnames = ['localhost', '127.0.0.1', 'LAP-CDE']
    return hostname in local_hostnames


def load_json_config(file_path):
    # Loads a JSON file and returns the corresponding map
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Erreur lors du chargement du fichier {file_path}: {e}")
        return {}


def extract_paths(config_data, key_name):
    # Extracts paths for a given key and returns a map
    extracted_map = {}
    for manual, paths in config_data.items():
        extracted_map[manual] = paths.get(key_name, "")
    return extracted_map
