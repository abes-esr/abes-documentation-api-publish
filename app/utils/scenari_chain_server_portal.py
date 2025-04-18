import os
from datetime import datetime, time
from app.config import config
import logging
import scchainserver_6_3
import scenaripy_api as api
from scchainserver_6_3 import portal

logger = logging.getLogger('uvicorn.error')


class ScenariChainServerPortal:
    def __init__(self):
        try:
            self.server = scchainserver_6_3.portal.new_portal(
                override_props={"user": config.GENERATION_USER, "password": config.GENERATION_PASSWORD})
            logger.info(f"Connexion au serveur scenari effectuée : {self.server}")
            self.wsp_code = api.search_wsp_code(self.server, title_fragment=config.GENERATION_WORKSHOP)
            logger.info(f"Code de l'atelier {config.GENERATION_WORKSHOP} : {self.wsp_code}")
            self.gen_path = config.GENERATION_ZIP_PATH
        except Exception as e:
            logger.error(f"Erreur lors de l'appel au serveur scchainserver_6_3 : {e}")
            raise

    def generate(self, pub_uri):
        try:
            api.wsp_generate(self.server, self.wsp_code, ref_uri=pub_uri, code_gen_stack=config.GENERATION_GENERATOR,
                             props={"skin": config.GENERATION_SKIN}, local_file_path=self.gen_path)

            # Vérifier si le fichier est créé avec un timeout
            timeout = 60  # Temps maximum d'attente en secondes
            start_time = datetime.now().time()

            while not os.path.exists(self.gen_path):
                if datetime.now().time() - start_time > timeout:
                    logger.error(f"Timeout atteint : le fichier {self.gen_path} n'a pas été créé. [{pub_uri}]")
                    raise TimeoutError(f"Le fichier {self.gen_path} n'a pas été créé dans le délai imparti. [{pub_uri}]")

                logger.info(f"Attente de la création du fichier {config.GENERATION_ZIP_PATH}...")
                time.sleep(5)
            logger.info(f"Fichier {config.GENERATION_ZIP_PATH} généré")
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à api.wsp_generate : {e}")
            raise
