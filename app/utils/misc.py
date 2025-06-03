import hashlib
import os
import shutil
import socket
import logging
import json
from datetime import datetime

from app import config
from app.utils.scenari_chain_server_portal import ScenariChainServerPortal
import re

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

def calculate_file_checksum(zip_path):
    """Calculate the SHA-256 checksum of a ZIP file."""
    sha256 = hashlib.sha256()
    with open(zip_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def is_file_in_list(target_file_path, file_list):
    """Check if the target file has the same checksum as any file in the list."""
    target_checksum = calculate_file_checksum(target_file_path)

    for file_path in file_list:
        file_list_checksum = calculate_file_checksum(config.DOCUMENTATION_API_PUBLISH_LOCAL_BACKUP_PATH + file_path)
        if file_list_checksum == target_checksum:
            return True

    return False


def find_files(zip_file_name, directory_path):
    """Find files in the directory that match the partial name, ignoring the date in the filename."""
    # Regex pattern to match the partial nasme with any date format
    pattern = re.compile(r'.*' + re.escape(zip_file_name) + r'.*')

    matching_files = []
    # List all files in the directory
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path) and pattern.match(file_name):
            matching_files.append(file_name)

    return matching_files


def copy_file_to_directory(source_file, destination_directory):
    try:
        os.makedirs(destination_directory, exist_ok=True)

        shutil.copy(source_file, destination_directory)

        logger.info(f"Fichier {source_file} copié vers {destination_directory}")
    except Exception as e:
        logger.info(f"Erreur lors de la copie du fichier : {e}")


def get_formatted_time():
    now = datetime.now()
    formatted_time = now.strftime("_%Y-%m-%d_%H-%M-%S")
    return formatted_time

def write_report(result):
    file_path = config.DOCUMENTATION_API_PUBLISH_LOCAL_BACKUP_PATH + "rapport-de-publication_" + get_formatted_time() + ".log"
    with open(file_path, "w", encoding="utf-8") as file:
        for deployment in result:
            if 'name' in deployment:
                file.write(f"Nom: {deployment['name']}\n")
            if 'workshop' in deployment:
                file.write(f"Atelier: {deployment['workshop']}\n")
            if 'scenari_pub_path' in deployment:
                file.write(f"Chemin de publication Scenari: {deployment['scenari_pub_path']}\n")
            if 'status' in deployment:
                file.write(f"Statut: {deployment['status']}\n")
            if 'code' in deployment:
                file.write(f"Code: {deployment['code']}\n")
            if 'detail' in deployment:
                file.write(f"Détail: {deployment['detail']}\n")
            file.write("\n")

    logger.info(f"Le rapport a été écrit dans {file_path}")