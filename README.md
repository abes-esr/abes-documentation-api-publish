# abes-documentation-api-publish
[![build-test-pubtodockerhub](https://github.com/abes-esr/abes-documentation-api-publish/actions/workflows/build-test-pubtodockerhub.yml/badge.svg)](https://github.com/abes-esr/abes-documentation-api-publish/actions/workflows/build-test-pubtodockerhub.yml) [![Docker Pulls](https://img.shields.io/docker/pulls/abesesr/documentation.svg)](https://hub.docker.com/r/abesesr/documentation)


Cette API permet de générer des manuels depuis un atelier scenari de l'ABES puis de les déployer sur le serveur web http://documentation.abes.fr/ en purgeant le manuel existant. 
Elle permet d'effectuer des déploiements de masse ou à l'unité. Elle construit la liste des manuels selon les données du fichier config/configuration_noms_chemins_manuels.json

Les interfaces de l'API sont respectivement disponibles à ces adresses :
- https://documentation-publication.abes.fr
- https://documentation-publication-test.abes.fr
- https://documentation-publication-dev.abes.fr

## Prérequis

Python 3.11+

## Installation

### Étape 1 : Installer les Dépendances
Installez les dépendances Python nécessaires :

```Bash
pip install -r requirements.txt
pip install lib/scenaripy_api-6.4.0.tar.gz
pip install lib/branch/SCENARIchain-server_6.3.13final_python.tar.gz
```

### Étape 2 : Configurer les Variables d'Environnement
```Bash
cp ./.env_dist ./.env
```

## Lancer l'API Localement
Pour lancer l'API localement sans Docker :

```Bash
uvicorn app.main\:app --host 0.0.0.0 --port 8000 --reload
```

## Créer l'image docker
Passer le nom de l'environnement en argument (develop|test|main)
```Bash
docker build --build-arg DOCUMENTATION_API_PUBLISH_SCENARI_API_FOLDER=develop -t abes-documentation-api-publish .
```

## Accéder à l'API
L'API sera accessible à l'adresse http://localhost:8000. Vous pouvez interagir avec l'API via un navigateur web ou des outils comme Postman ou cURL.

## Utiliser Swagger UI
Accédez à http://localhost:8000/docs pour interagir avec l'API via l'interface Swagger.

## Endpoints
**GET /list/{workshop_key}** : Liste des manuels disponibles dans l'atelier.

**PUT /deploy/{workshop_key}** : Déclenche la génération d'un ou plusieurs manuels.<br>
Exemple : /deploy/atelier2?manuals=manuelBacon&manuals=manuelItem

**PUT /deploy_all/{workshop_key}** : Déclenche la génération de tous les manuels de l'atelier.

**PUT /purge/{workshop_key}** : Supprime les dossiers et fichiers web générés par scenari (ne supprime pas les ressources de formation).<br>
Exemple : /purge/atelier2?manuals=ManuelPeriscope&manuals=ManuelLicencesNationales&manuals=ManuelItem

**GET /list/workshops** : Liste des ateliers disponibles et du nom de la clé à utiliser dans la route de l'atelier.
