import os
from datetime import time
from app.config import config
import logging
import scchainserver_6_3
import scenaripy_api as api
from scchainserver_6_3 import portal

logger = logging.getLogger(__name__)

class ScenariChainServerPortal:
    def __init__(self):
        self.server = scchainserver_6_3.portal.new_portal(override_props={"user": config.GENERATION_USER, "password": config.GENERATION_PASSWORD})
        self.wsp_code = api.search_wsp_code(self.server, title_fragment= config.GENERATION_WORKSHOP)
        self.gen_path = config.GENERATION_ZIP_PATH

    def generate(self, pub_uri):
        api.wsp_generate(self.server, self.wsp_code, ref_uri=pub_uri, code_gen_stack=config.GENERATION_GENERATOR, props={"skin": config.GENERATION_SKIN}, local_file_path=self.gen_path)
        #TODO Gérer les retours erreur
        while not os.path.exists(self.gen_path):
            logger.info("Attente de la création du fichier gen.zip...")
            time.sleep(5)  # Attendre 5 secondes avant de revérifier
