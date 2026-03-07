from importlib.metadata import PackageNotFoundError, version

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..k8s_client import K8sClient, get_k8s_client

API_VERSION = "1"

try:
    KLANCES_VERSION = version("klances")
except PackageNotFoundError:
    KLANCES_VERSION = "unknown"


class StatusResponse(BaseModel):
    status: str
    klances_version: str
    api_version: str
    cluster_reachable: bool
    cluster_error: str | None = None


router = APIRouter()


@router.get("/status", response_model=StatusResponse)
def get_status(k8s: K8sClient = Depends(get_k8s_client)):
    reachable, error = k8s.check_connection()
    return StatusResponse(
        status="ready",
        klances_version=KLANCES_VERSION,
        api_version=API_VERSION,
        cluster_reachable=reachable,
        cluster_error=error,
    )
