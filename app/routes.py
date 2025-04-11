from fastapi import APIRouter, HTTPException, Query
from .services.deployment_service import deploy_manuals, list_manuals, deploy_all_manuals, purge_directory
import logging

router = APIRouter()

@router.get("/deploy")
async def deploy(manuels: list[str] = Query(...)):
    logging.info("{str(manuels)}")
    status = deploy_manuals(manuels)
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Deployment failed")
    return status

@router.get("/list")
async def list_available_manuals():
    return list_manuals()

@router.get("/deploy_all")
async def deploy_all():
    status = deploy_all_manuals()
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Deployment failed")
    return status

@router.get("/purge_directory")
async def purge_dir(manuel: str = Query(...)):
    status = purge_directory(manuel)
    if not status["success"]:
        raise HTTPException(status_code=500, detail="Deployment failed")
    return status

def init_routes(app):
    app.include_router(router, prefix="/api")
