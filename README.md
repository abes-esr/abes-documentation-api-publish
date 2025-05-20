# abes-documentation-api-publish
[![build-test-pubtodockerhub](https://github.com/abes-esr/abes-documentation-api-publish/actions/workflows/build-test-pubtodockerhub.yml/badge.svg)](https://github.com/abes-esr/abes-documentation-api-publish/actions/workflows/build-test-pubtodockerhub.yml) [![Docker Pulls](https://img.shields.io/docker/pulls/abesesr/documentation.svg)](https://hub.docker.com/r/abesesr/documentation)


Cette API permet de générer des manuels depuis un atelier scenari de l'ABES puis de les déployer sur le serveur web http://documentation.abes.fr/ en purgeant le manuel existant. 
Elle permet d'effectuer des déploiements de masse ou à l'unité. Elle construit la liste des manuels selon les données du fichier config/configuration_noms_chemins_manuels.json

L'API est disponible à ces adresses :
- https://documentation.abes.fr/api/v1/
- https://documentation-test.abes.fr/api/v1/
- https://documentation-dev.abes.fr/api/v1/

L'interface utilisateurs quant à elle est ici :
- https://documentation.abes.fr/dashboard/access
- https://documentation-test.abes.fr/dashboard/access
- https://documentation-dev.abes.fr/dashboard/access

## Prérequis

Python 3.11+

## Installation

### Étape 1 : Installer les Dépendances
Installez les dépendances Python nécessaires :

```Bash
pip install -r requirements.txt
pip install lib/scenaripy_api-6.4.0.tar.gz
pip install lib/branch_name/SCENARIchain-server_6.3.13final_python.tar.gz
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

## Utiliser Swagger UI
Accédez à http://localhost:8000/dashboard/access pour interagir avec l'API via l'interface Swagger.

## Endpoints

### Liste des Manuels Disponibles
> **GET /list/{workshop_key}**
> - **Description** : Récupère la liste des manuels disponibles dans l'atelier spécifié.
> - **Paramètres** :
>     - `workshop_key` (string, requis) : La clé de l'atelier pour lequel récupérer les manuels.
> - **Exemple de Requête** :
>   GET /deploy/atelier2?manuals=manuelBacon&manuals=manuelItem

### Déclencher la Génération de Manuels
> **PUT /deploy/{workshop_key}**
> - **Description** : Déclenche la génération d'un ou plusieurs manuels pour l'atelier spécifié.
> - **Paramètres** :
>     - `workshop_key` (string, requis) : La clé de l'atelier pour lequel générer les manuels.
>     - `manuals` (string, optionnel) : Le nom des manuels à générer. Peut être spécifié plusieurs fois.
> - **Exemple de Requête** :
>   PUT /deploy/atelier2?manuals=manuelBacon&manuals=manuelItem

### Déclencher la Génération de Tous les Manuels
> **PUT /deploy_all/{workshop_key}**
> - **Description** : Déclenche la génération de tous les manuels de l'atelier spécifié.
> - **Paramètres** :
>     - `workshop_key` (string, requis) : La clé de l'atelier pour lequel générer tous les manuels.
> - **Exemple de Requête** :
>   PUT /deploy_all/atelier1

### Supprimer les Dossiers et Fichiers Web Générés
> **PUT /purge/{workshop_key}**
> - **Description** : Supprime les dossiers et fichiers web générés par scenari (ne supprime pas les ressources de formation).
> - **Paramètres** :
>     - `workshop_key` (string, requis) : La clé de l'atelier pour lequel supprimer les fichiers.
>     - `manuals` (string, optionnel) : Le nom des manuels dont les fichiers doivent être supprimés. Peut être spécifié plusieurs fois.
> - **Exemple de Requête** :
>   PUT /purge/atelier2?manuals=ManuelPeriscope&manuals=ManuelLicencesNationales&manuals=ManuelItem

### Liste des Ateliers Disponibles
> **GET /list/workshops**
> - **Description** : Récupère la liste des ateliers disponibles et du nom de la clé à utiliser dans la route de l'atelier.
> - **Exemple de Requête** :
>   GET /list/workshops

### Liste des Ateliers avec Erreurs
> **GET /list/errors**
> - **Description** : Récupère la liste des noms d'ateliers présents dans le fichier de configuration, pour lesquels l'API a rencontré une erreur en appelant le serveur scenarichain.
> - **Exemple de Requête** :
>   GET /list/errors

### Vérification du Nom de l'Atelier
> **GET /list/check-workshop-name**
> - **Description** : Vérifie si un nom d'atelier est valide ou disponible.
> - **Paramètres** :
>     - `wsp_name` (string, requis) : Le nom de l'atelier à vérifier.
> - **Exemple de Requête** :
>   GET /list/check-workshop-name?wsp_name=Documentation