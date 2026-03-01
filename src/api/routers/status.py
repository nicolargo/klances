from importlib.metadata import version, PackageNotFoundError

from fastapi import APIRouter
from pydantic import BaseModel

API_VERSION = "1"

try:
    KLANCES_VERSION = version("klances")
except PackageNotFoundError:
    KLANCES_VERSION = "unknown"


class StatusResponse(BaseModel):
    status: str
    klances_version: str
    api_version: str


router = APIRouter()


@router.get("/status", response_model=StatusResponse)
def get_status():
    return StatusResponse(
        status="ready",
        klances_version=KLANCES_VERSION,
        api_version=API_VERSION,
    )
