from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from urllib3.exceptions import MaxRetryError

from .k8s_client import K8sUnavailableError
from .routers import cluster, namespaces, nodes, pods, status
from .version import API_VERSION, KLANCES_VERSION

API_PREFIX = f"/api/{API_VERSION}"

app = FastAPI(
    title="Klances API",
    description="Kubernetes cluster monitoring REST API",
    version=KLANCES_VERSION,
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
)


@app.exception_handler(K8sUnavailableError)
async def k8s_config_error_handler(
    request: Request, exc: K8sUnavailableError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "detail": f"Kubernetes configuration error: {exc}",
            "cluster_reachable": False,
        },
    )


@app.exception_handler(MaxRetryError)
async def k8s_unreachable_handler(request: Request, exc: MaxRetryError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Kubernetes cluster unreachable",
            "cluster_reachable": False,
        },
    )


app.include_router(status.router, prefix=API_PREFIX, tags=["status"])
app.include_router(cluster.router, prefix=API_PREFIX, tags=["cluster"])
app.include_router(nodes.router, prefix=API_PREFIX, tags=["nodes"])
app.include_router(namespaces.router, prefix=API_PREFIX, tags=["namespaces"])
app.include_router(pods.router, prefix=API_PREFIX, tags=["pods"])


@app.get("/", include_in_schema=False)
def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/frontend/")


# Serve the built Vue.js frontend under /frontend/
# Check relative to source tree first, then relative to working directory
_candidates = [
    Path(__file__).parent.parent / "frontend" / "dist",
    Path.cwd() / "src" / "frontend" / "dist",
]
_frontend_dist = next((p for p in _candidates if p.is_dir()), None)
if _frontend_dist:
    app.mount(
        "/frontend",
        StaticFiles(directory=str(_frontend_dist), html=True),
        name="frontend",
    )
