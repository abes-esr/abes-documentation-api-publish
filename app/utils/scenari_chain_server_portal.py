import os
from time import monotonic as timer
import time
from app.config import config
import logging
import scchainserver_6_4
import scenaripy_api as api
from scchainserver_6_4 import portal

logger = logging.getLogger('uvicorn.error')


class ScenariChainServerPortal:
    def __init__(self, workshop_title):
        try:
            self.server = scchainserver_6_3.portal.new_portal(
                override_props={"user": config.DOCUMENTATION_API_PUBLISH_USER, "password": config.DOCUMENTATION_API_PUBLISH_PASSWORD})
            logger.info(f"Connexion au serveur scenari effectuée : {self.server}")
            logger.info(f"Recherche de l'atelier : {workshop_title}")
            self.wsp_code = api.search_wsp_code(self.server, title_fragment=workshop_title)
            logger.info(f"Code de l'atelier {workshop_title} : {self.wsp_code}")
            self.gen_path = config.DOCUMENTATION_API_PUBLISH_ZIP_PATH
        except Exception as e:
            logger.error(f"Erreur lors de l'appel au serveur scchainserver_6_3 : {e}")
            raise

    def generate(self, pub_uri, generator_code):
        try:
            if os.path.exists(self.gen_path):
                logger.info(f"Suppression de {self.gen_path}")
                os.remove(self.gen_path)
            # Warning function wsp_generate does not raise exceptions but logs errors though
            data = api.wsp_generate(self.server, self.wsp_code, ref_uri=pub_uri, code_gen_stack=generator_code,
                             props={"skin": config.DOCUMENTATION_API_PUBLISH_SKIN}, local_file_path=self.gen_path)

            # timeout checks creation of file
            timeoutSet = 15 # seconds
            timeout = timer() + timeoutSet

            while not os.path.exists(self.gen_path):
                if timer() > timeout:
                    logger.error(f"Erreur dans la génération de [{pub_uri}]")
                    raise TimeoutError(f"Erreur dans la génération de [{pub_uri}]")

                logger.info(f"Attente de la création du fichier {config.DOCUMENTATION_API_PUBLISH_ZIP_PATH}...")
                time.sleep(5)
            logger.info(f"Fichier {config.DOCUMENTATION_API_PUBLISH_ZIP_PATH} généré")
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à api.wsp_generate : {e}")
            raise