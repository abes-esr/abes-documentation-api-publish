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
