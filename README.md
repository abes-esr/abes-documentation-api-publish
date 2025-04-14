# abes-documentation-api-publish
[![build-test-pubtodockerhub](https://github.com/abes-esr/abes-documentation-api-publish/actions/workflows/build-test-pubtodockerhub.yml/badge.svg)](https://github.com/abes-esr/abes-documentation-api-publish/actions/workflows/build-test-pubtodockerhub.yml) [![Docker Pulls](https://img.shields.io/docker/pulls/abesesr/abes-documentation-api-publish.svg)](https://hub.docker.com/r/abesesr/abes-documentation-api-publish/)


Cette API permet de générer des manuels depuis un atelier scenari de l'ABES puis de les déployer sur le serveur web http://documentation.abes.fr/ en purgeant le manuel existant. 
Elle permet d'effectuer des déploiements de masse ou à l'unité.

## Prérequis

Python 3.11+

## Installation

### Étape 1 : Installer les Dépendances
Installez les dépendances Python nécessaires :

```Bash
pip install -r requirements.txt
pip install lib/
pip install lib/
```

### Étape 3 : Configurer les Variables d'Environnement
```Bash
cp ./docker/env_placeholders ./.env
```

## Lancer l'API Localement
Pour lancer l'API localement sans Docker :

```Bash
uvicorn app.main\:app --host 0.0.0.0 --port 8000 --reload
```

## Accéder à l'API
L'API sera accessible à http://localhost:8000. Vous pouvez interagir avec l'API via un navigateur web ou des outils comme Postman ou cURL.

## Utiliser Swagger UI
Accédez à http://localhost:8000/docs pour interagir avec l'API via l'interface Swagger.

## Endpoints
GET /list : Liste des manuels disponibles.
PUT /deploy : Déclenche la génération d'un ou plusieurs manuels.
PUT /deploy_all : Déclenche la génération de tous les manuels.
PUT /purge-directory : Supprime les dossiers et fichiers web générés par scenari (ne supprime pas les ressources de formation).