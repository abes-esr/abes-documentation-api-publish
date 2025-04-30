import unittest
import os
import logging

from app.config import config
from app.services.deployment_service import purge_directory

logger = logging.getLogger('uvicorn.error')


class TestOperations(unittest.TestCase):

    def setUp(self):
        # Crée un répertoire temporaire pour les tests
        self.test_dir = ["aideperiscope/skin", "aideperiscope/res", "aideperiscope/co", "aideperiscope/lib-md", "aideperiscope/meta", "aideperiscope/lib-sc"]
        for directory_name in self.test_dir:
            try:
                os.makedirs(config.DOCUMENTATION_API_PUBLISH_LOCAL_PATH + directory_name, exist_ok=True)
                self.assertTrue(os.path.exists(config.DOCUMENTATION_API_PUBLISH_LOCAL_PATH + directory_name))
            except Exception as e:
                logger.error(f"Erreur lors de la création du répertoire {directory_name}: {e}")

    def test_purge_directory(self):
        self.setUp()
        purge_directory('ManuelPeriscope')

        for directory_name in self.test_dir:
            self.assertFalse(os.path.exists(config.DOCUMENTATION_API_PUBLISH_LOCAL_PATH + directory_name))

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, mock_open
import json
import os

# Importer les fonctions à tester
from your_module import load_json_config, extract_paths

class TestConfigLoading(unittest.TestCase):

    def setUp(self):
        # Définir un fichier JSON mock
        self.mock_json_data = {
            "ManuelPeriscope": {
                "cheminScenari": "/ManuelPeriscopeV2/0-Structure/ManuelPeriscope.pub",
                "cheminDeploiement": "aideperiscope/"
            },
            "ManuelLicencesNationales": {
                "cheminScenari": "/ManuelLicencesNationales/0-Structure/ManuelLicencesNationales.pub",
                "cheminDeploiement": "aidelicencesnationales/"
            }
        }

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps(mock_json_data))
    def test_load_json_config(self, mock_file):
        # Chemin fictif pour le test
        file_path = 'fake_path/configuration_noms_chemins_manuels.json'

        # Appeler la fonction à tester
        result = load_json_config(file_path)

        # Vérifier que le résultat correspond au JSON mock
        self.assertEqual(result, self.mock_json_data)

    def test_extract_paths(self):
        # Utiliser le JSON mock pour tester extract_paths
        scenari_map = extract_paths(self.mock_json_data, "cheminScenari")
        deployment_map = extract_paths(self.mock_json_data, "cheminDeploiement")

        # Vérifier que les chemins sont correctement extraits
        expected_scenari_map = {
            "ManuelPeriscope": "/ManuelPeriscopeV2/0-Structure/ManuelPeriscope.pub",
            "ManuelLicencesNationales": "/ManuelLicencesNationales/0-Structure/ManuelLicencesNationales.pub"
        }
        expected_deployment_map = {
            "ManuelPeriscope": "aideperiscope/",
            "ManuelLicencesNationales": "aidelicencesnationales/"
        }

        self.assertEqual(scenari_map, expected_scenari_map)
        self.assertEqual(deployment_map, expected_deployment_map)

if __name__ == '__main__':
    unittest.main()
